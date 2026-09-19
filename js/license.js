/* license.js -- free/pro tier gate for Regen Farm Field Log.
 *
 * The free tier keeps ONE paddock plus the whole logging/timeline surface.
 * A $29 one-time licence unlocks unlimited paddocks and the audit PDF export.
 *
 * TWO credentials are accepted, on purpose:
 *
 *   1. A PER-SALE LICENCE KEY, checked against Gumroad's PUBLIC
 *      POST /v2/licenses/verify endpoint. That endpoint takes product_id +
 *      license_key and needs NO seller token, which is what lets a static,
 *      backend-free app verify a real licence without shipping any secret to
 *      the browser. This is the primary mechanism.
 *
 *   2. A BUYER UNLOCK CODE, delivered with the purchase. Per-sale licence keys
 *      must be switched on in the seller UI; until they are, no per-sale key
 *      exists for a buyer to enter, so a key-only gate would take payment and
 *      hand the buyer nothing. This second route keeps the product deliverable
 *      either way. Once per-sale keys are on, route 1 works with no code change
 *      and route 2 retires by deleting UNLOCK_SHA256.
 *
 * OFFLINE-FIRST: this is a PWA used in a field with no signal. A licence is
 * verified ONCE over the network, then cached in localStorage and trusted
 * offline afterwards. Verification is never required to open the app or to read
 * existing entries -- losing signal must never lock someone out of their own
 * records.
 *
 * HONEST LIMIT, so nobody mistakes this for DRM: every check here runs in the
 * browser, so anyone with devtools can set the cache key by hand. That is true
 * of every client-side licence at this price. The gate is honesty-priced, not
 * tamper-proof; making it tamper-proof would need a server this app
 * deliberately does not have.
 */

const LICENSE_STORAGE_KEY = 'regenFieldLog.license.v1';
const GUMROAD_PRODUCT_ID = 'hw4DoQRSMi1rwlbBcp9clQ==';
const GUMROAD_PRODUCT_URL = 'https://wealthywellness0.gumroad.com/l/regenfieldlog';
const GUMROAD_VERIFY_URL = 'https://api.gumroad.com/v2/licenses/verify';

// SHA-256 of the buyer unlock code. The plaintext is NOT in this file, so
// reading the source does not hand out the code -- it only proves one exists.
const UNLOCK_SHA256 = 'd16f45be7467189fecaa7ba3e4e8e78b36fca1144a4804e99122a7e76b066065';

const FREE_PADDOCK_LIMIT = 1;

/* ---------- pure decision logic (unit-testable, no DOM, no network) ---------- */

/**
 * Can another paddock be created?
 * Pure so selftest.js can drive it without a browser.
 */
function canAddPaddock(paddockCount, isPro) {
  return isPro || paddockCount < FREE_PADDOCK_LIMIT;
}

/** Can the audit PDF be exported? Pro-only -- it is the thing being sold. */
function canExportPdf(isPro) {
  return !!isPro;
}

/**
 * Decide a tier from a Gumroad /licenses/verify response body.
 * Pure. Kept separate from the fetch so the refund/chargeback rules can be
 * tested without hitting the network.
 *
 * A sale that was refunded, disputed or cancelled is NOT a live licence --
 * Gumroad keeps returning success:true for those, with the state in the
 * purchase object, so checking only `success` would honour refunded keys.
 */
function tierFromVerifyResponse(body) {
  if (!body || body.success !== true) return 'free';
  const p = body.purchase || {};
  if (p.refunded || p.disputed || p.chargebacked) return 'free';
  if (p.subscription_cancelled_at || p.subscription_failed_at) return 'free';
  return 'pro';
}

/* ---------- storage ---------- */

function readCache() {
  try {
    const raw = localStorage.getItem(LICENSE_STORAGE_KEY);
    if (!raw) return null;
    const obj = JSON.parse(raw);
    return obj && obj.tier === 'pro' ? obj : null;
  } catch (e) {
    // Private mode / blocked site data / corrupt JSON. Degrade to free, never throw:
    // a storage failure must not stop the app opening.
    return null;
  }
}

function writeCache(obj) {
  try {
    localStorage.setItem(LICENSE_STORAGE_KEY, JSON.stringify(obj));
    return true;
  } catch (e) {
    return false;
  }
}

async function sha256Hex(s) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s));
  return Array.from(new Uint8Array(buf)).map((b) => b.toString(16).padStart(2, '0')).join('');
}

/* ---------- public API ---------- */

const License = {
  PRODUCT_URL: GUMROAD_PRODUCT_URL,
  FREE_PADDOCK_LIMIT,
  canAddPaddock,
  canExportPdf,
  tierFromVerifyResponse,

  _cache: undefined,

  /** Synchronous, safe to call from render(). Reads the cache once, then memoises. */
  isPro() {
    if (this._cache === undefined) this._cache = readCache();
    return !!this._cache;
  },

  info() {
    this.isPro();
    return this._cache;
  },

  /**
   * Try to turn `code` into a pro licence.
   * Returns {ok, message}. Never throws -- the caller shows the message.
   */
  async activate(code) {
    const key = (code || '').trim();
    if (!key) return { ok: false, message: 'Enter your code first.' };

    // Route 2: buyer unlock code. Checked first because it works offline and
    // costs no network round-trip.
    try {
      if ((await sha256Hex(key.toUpperCase())) === UNLOCK_SHA256) {
        this._cache = { tier: 'pro', via: 'unlock-code', activatedAt: new Date().toISOString() };
        writeCache(this._cache);
        return { ok: true, message: 'Unlocked. Thank you!' };
      }
    } catch (e) {
      // crypto.subtle is unavailable on insecure origins (plain http). Fall
      // through to the Gumroad route rather than failing the whole activation.
    }

    // Route 1: Gumroad per-sale licence key.
    let body;
    try {
      const res = await fetch(GUMROAD_VERIFY_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          product_id: GUMROAD_PRODUCT_ID,
          license_key: key,
          increment_uses_count: 'false',
        }),
      });
      body = await res.json();
    } catch (e) {
      return { ok: false, message: 'Could not reach Gumroad. Check your signal and try again.' };
    }

    if (tierFromVerifyResponse(body) === 'pro') {
      this._cache = { tier: 'pro', via: 'gumroad-license', activatedAt: new Date().toISOString() };
      writeCache(this._cache);
      return { ok: true, message: 'Licence verified. Thank you!' };
    }

    const p = (body && body.purchase) || {};
    if (p.refunded || p.disputed || p.chargebacked) {
      return { ok: false, message: 'That order was refunded, so the licence is closed.' };
    }
    return { ok: false, message: 'That code did not work. Check it and try again.' };
  },

  /** Used by the selftest page and by support, never by the normal UI. */
  deactivate() {
    this._cache = null;
    try { localStorage.removeItem(LICENSE_STORAGE_KEY); } catch (e) {}
  },
};

if (typeof window !== 'undefined') window.License = License;
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { canAddPaddock, canExportPdf, tierFromVerifyResponse, FREE_PADDOCK_LIMIT };
}
