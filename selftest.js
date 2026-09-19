/* selftest.js -- proves the licence gate can return the answer it exists to detect.
 *
 * FALSIFIABILITY LAW (2026-08-14): a gate that never blocks is indistinguishable
 * from no gate at all. So this does not only check that a paying user gets
 * through -- it checks that a FREE user is STOPPED, and it deliberately feeds
 * the refund/chargeback shapes that a naive `if (body.success)` check would wave
 * through. If someone later "simplifies" tierFromVerifyResponse down to a
 * success check, cases 9-12 go red.
 *
 * Run:  node selftest.js      (exit 0 = all pass, 1 = a failure)
 */
const L = require('./js/license.js');

let pass = 0, fail = 0;
function check(name, got, want) {
  const ok = got === want;
  ok ? pass++ : fail++;
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}  (got ${got}, want ${want})`);
}

console.log('--- paddock limit: the gate must BLOCK, not just allow ---');
check('free, 0 paddocks -> can add the first',      L.canAddPaddock(0, false), true);
check('free, 1 paddock  -> BLOCKED (the sale)',     L.canAddPaddock(1, false), false);
check('free, 5 paddocks -> BLOCKED',                L.canAddPaddock(5, false), false);
check('pro,  1 paddock  -> allowed',                L.canAddPaddock(1, true),  true);
check('pro,  99 paddocks -> allowed',               L.canAddPaddock(99, true), true);
check('free limit is exactly 1',                    L.FREE_PADDOCK_LIMIT,      1);

console.log('--- pdf export ---');
check('free -> export BLOCKED',                     L.canExportPdf(false), false);
check('pro  -> export allowed',                     L.canExportPdf(true),  true);

console.log('--- verify-response parsing: the refund cases a success-check would miss ---');
const t = L.tierFromVerifyResponse;
check('live purchase -> pro',        t({ success: true, purchase: {} }),                        'pro');
check('refunded -> free',            t({ success: true, purchase: { refunded: true } }),        'free');
check('chargebacked -> free',        t({ success: true, purchase: { chargebacked: true } }),    'free');
check('disputed -> free',            t({ success: true, purchase: { disputed: true } }),        'free');
check('cancelled sub -> free',       t({ success: true, purchase: { subscription_cancelled_at: '2026-09-01' } }), 'free');
check('success:false -> free',       t({ success: false }),                                     'free');
check('empty body -> free',          t({}),                                                     'free');
check('null body -> free',           t(null),                                                   'free');
check('garbage body -> free',        t({ success: 'yes' }),                                     'free');

console.log(`\n${fail === 0 ? 'SELFTEST PASS' : 'SELFTEST FAIL'} — ${pass} passed, ${fail} failed`);
process.exit(fail === 0 ? 0 : 1);
