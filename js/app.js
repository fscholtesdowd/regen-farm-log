const root = document.getElementById('view-root');
const toastEl = document.getElementById('toast');

const state = {
  view: 'log',
  paddocks: [],
  livestockGroups: [],
  entryType: 'note',
  pendingPhotos: [], // {id, blob, dataUrl}
  timelineFilter: { paddockId: '', type: '' },
  objectUrls: [],
  reportObjectUrls: [],
};

function toast(msg) {
  toastEl.textContent = msg;
  toastEl.classList.add('show');
  clearTimeout(toast._t);
  toast._t = setTimeout(() => toastEl.classList.remove('show'), 1800);
}

function todayStr() {
  const d = new Date();
  return d.toISOString().slice(0, 10);
}

function formatDate(dateStr) {
  const [y, m, d] = dateStr.split('-').map(Number);
  const dt = new Date(y, m - 1, d);
  return dt.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
}

function daysBetween(dateStr) {
  const [y, m, d] = dateStr.split('-').map(Number);
  const then = new Date(y, m - 1, d);
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  then.setHours(0, 0, 0, 0);
  return Math.round((now - then) / 86400000);
}

function escapeHtml(s) {
  return (s || '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

const ENTRY_BADGES = {
  note: ['badge-note', '📝 Note'],
  grazing: ['badge-grazing', '🐄 Grazing'],
  input: ['badge-input', '🌾 Input'],
  cover_crop: ['badge-cover_crop', '🌿 Cover Crop'],
};

function entryDetailText(e) {
  if (e.type === 'grazing') {
    return `${groupName(e.livestockGroupId)} moved ${e.moveType === 'in' ? 'IN' : 'OUT'}`;
  }
  if (e.type === 'input') {
    let s = e.inputType || 'Input';
    if (e.quantity) s += ' — ' + e.quantity;
    if (e.source) s += ' (source: ' + e.source + ')';
    return s;
  }
  if (e.type === 'cover_crop') {
    const actionLabel = { planted: 'Planted', terminated: 'Terminated', assessed: 'Assessed' }[e.cropAction] || e.cropAction;
    let s = `${actionLabel}: ${e.crop || 'cover crop'}`;
    if (e.cropRate) s += ' — ' + e.cropRate;
    return s;
  }
  return '';
}

function paddockName(id) {
  const p = state.paddocks.find((p) => p.id === id);
  return p ? p.name : '(unknown paddock)';
}

function groupName(id) {
  const g = state.livestockGroups.find((g) => g.id === id);
  return g ? g.name : '(unknown group)';
}

async function loadRefData() {
  state.paddocks = (await DB.getAll('paddocks')).sort((a, b) => a.name.localeCompare(b.name));
  state.livestockGroups = (await DB.getAll('livestockGroups')).sort((a, b) => a.name.localeCompare(b.name));
}

function revokeObjectUrls() {
  state.objectUrls.forEach((u) => URL.revokeObjectURL(u));
  state.objectUrls = [];
}

// ---------- Navigation ----------

document.querySelectorAll('.tab-btn').forEach((btn) => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');
    state.view = btn.dataset.view;
    render();
  });
});

async function render() {
  revokeObjectUrls();
  await loadRefData();
  if (state.view === 'log') return renderLog();
  if (state.view === 'timeline') return renderTimeline();
  if (state.view === 'dashboard') return renderDashboard();
  if (state.view === 'export') return renderExport();
  if (state.view === 'manage') return renderManage();
  if (state.view === 'unlock') return renderUnlock();
}

// ---------- Free / Pro gate ----------
// One helper per gated action so the limit is expressed in exactly one place.
// Both call into License's pure predicates, which selftest.js drives directly.

function paddockLimitReached() {
  return !License.canAddPaddock(state.paddocks.length, License.isPro());
}

/** The upsell shown wherever a gated action is blocked. */
function upgradeCard(reason) {
  return `
    <div class="card upsell">
      <div class="upsell-title">🔒 ${escapeHtml(reason)}</div>
      <div class="entry-body">The free log keeps ${License.FREE_PADDOCK_LIMIT} paddock.
      One payment of $29 unlocks every paddock and the audit PDF, for good.</div>
      <a class="btn block" href="${License.PRODUCT_URL}" target="_blank" rel="noopener">Unlock for $29</a>
      <button class="btn secondary block" data-goto-unlock>I already bought it</button>
    </div>
  `;
}

/** Wire any [data-goto-unlock] button rendered by upgradeCard(). */
function bindUpgradeCard(scope) {
  (scope || document).querySelectorAll('[data-goto-unlock]').forEach((btn) => {
    btn.addEventListener('click', () => switchTab('unlock'));
  });
}

function switchTab(view) {
  document.querySelectorAll('.tab-btn').forEach((b) => b.classList.toggle('active', b.dataset.view === view));
  state.view = view;
  render();
}

// ---------- Log (entry form) ----------

function renderLog() {
  const paddockOptions = state.paddocks.map((p) => `<option value="${p.id}">${escapeHtml(p.name)}</option>`).join('');
  const groupOptions = state.livestockGroups.map((g) => `<option value="${g.id}">${escapeHtml(g.name)}</option>`).join('');

  root.innerHTML = `
    <h2>New Log Entry</h2>
    <div class="type-switch">
      <button data-type="note" class="${state.entryType === 'note' ? 'active' : ''}">📝 Note</button>
      <button data-type="grazing" class="${state.entryType === 'grazing' ? 'active' : ''}">🐄 Grazing</button>
      <button data-type="input" class="${state.entryType === 'input' ? 'active' : ''}">🌾 Soil/Input</button>
      <button data-type="cover_crop" class="${state.entryType === 'cover_crop' ? 'active' : ''}">🌿 Cover Crop</button>
    </div>

    <div class="card">
      <label>Date</label>
      <input type="date" id="f-date" value="${todayStr()}">

      <label>Paddock / Field</label>
      ${state.paddocks.length ? `
        <select id="f-paddock">${paddockOptions}</select>
      ` : `<div class="entry-body" style="margin-bottom:8px;">No paddocks yet.</div>`}
      <div id="quick-add-paddock" style="margin-top:6px;">
        ${paddockLimitReached() ? `
          <div class="locked-inline">🔒 Free keeps ${License.FREE_PADDOCK_LIMIT} paddock.
          <a href="#" data-goto-unlock>Unlock more</a></div>
        ` : `
          <input type="text" id="new-paddock-name" placeholder="Add new paddock name…" style="display:inline-block;width:70%;">
          <button class="btn secondary small" id="btn-add-paddock" style="width:28%;float:right;">+ Add</button>
          <div style="clear:both;"></div>
        `}
      </div>

      ${state.entryType === 'grazing' ? `
        <label>Livestock Group</label>
        ${state.livestockGroups.length ? `<select id="f-group">${groupOptions}</select>` : `<div class="entry-body" style="margin-bottom:8px;">No livestock groups yet.</div>`}
        <div style="margin-top:6px;">
          <input type="text" id="new-group-name" placeholder="Add new livestock group…" style="display:inline-block;width:70%;">
          <button class="btn secondary small" id="btn-add-group" style="width:28%;float:right;">+ Add</button>
          <div style="clear:both;"></div>
        </div>
        <label>Move</label>
        <select id="f-move">
          <option value="in">Moved IN (grazing started)</option>
          <option value="out">Moved OUT (grazing ended / rest starts)</option>
        </select>
      ` : ''}

      ${state.entryType === 'input' ? `
        <label>Input / Amendment type</label>
        <input type="text" id="f-input-type" placeholder="e.g. compost, lime, biochar">
        <label>Quantity</label>
        <input type="text" id="f-quantity" placeholder="e.g. 2 tons, 50 lbs">
        <label>Source (optional, for audit trail)</label>
        <input type="text" id="f-source" placeholder="e.g. supplier name / OMRI-listed product">
      ` : ''}

      ${state.entryType === 'cover_crop' ? `
        <label>Crop / Mix</label>
        <input type="text" id="f-crop" placeholder="e.g. crimson clover + oats">
        <label>Action</label>
        <select id="f-crop-action">
          <option value="planted">Planted</option>
          <option value="terminated">Terminated</option>
          <option value="assessed">Assessed / growth check</option>
        </select>
        <label>Rate / Method (optional)</label>
        <input type="text" id="f-crop-rate" placeholder="e.g. 30 lbs/acre, drilled">
      ` : ''}

      <label>Notes</label>
      <textarea id="f-notes" placeholder="Observations, conditions, details…"></textarea>

      <label>Photos</label>
      <input type="file" id="f-photos" accept="image/*" capture="environment" multiple>
      <div class="photo-thumbs" id="photo-thumbs"></div>

      <button class="btn block" id="btn-save">Save Entry</button>
    </div>
  `;

  document.querySelectorAll('.type-switch button').forEach((btn) => {
    btn.addEventListener('click', () => {
      state.entryType = btn.dataset.type;
      renderLog();
    });
  });

  bindUpgradeCard(root);

  const addPaddockBtn = document.getElementById('btn-add-paddock');
  if (addPaddockBtn) addPaddockBtn.addEventListener('click', async () => {
    const input = document.getElementById('new-paddock-name');
    const name = input.value.trim();
    if (!name) return;
    // Re-check at the moment of the write, not just at render: the button could
    // have been rendered before a paddock was added in another tab.
    if (paddockLimitReached()) {
      toast('Free keeps 1 paddock — unlock for more');
      return renderLog();
    }
    const p = { id: DB.genId(), name, createdAt: Date.now() };
    await DB.put('paddocks', p);
    state.paddocks.push(p);
    state.paddocks.sort((a, b) => a.name.localeCompare(b.name));
    renderLog();
    toast(`Added paddock "${name}"`);
    setTimeout(() => {
      const sel = document.getElementById('f-paddock');
      if (sel) sel.value = p.id;
    }, 0);
  });

  const groupBtn = document.getElementById('btn-add-group');
  if (groupBtn) {
    groupBtn.addEventListener('click', async () => {
      const input = document.getElementById('new-group-name');
      const name = input.value.trim();
      if (!name) return;
      const g = { id: DB.genId(), name, createdAt: Date.now() };
      await DB.put('livestockGroups', g);
      state.livestockGroups.push(g);
      state.livestockGroups.sort((a, b) => a.name.localeCompare(b.name));
      renderLog();
      toast(`Added livestock group "${name}"`);
      setTimeout(() => {
        const sel = document.getElementById('f-group');
        if (sel) sel.value = g.id;
      }, 0);
    });
  }

  document.getElementById('f-photos').addEventListener('change', async (e) => {
    for (const file of e.target.files) {
      const id = DB.genId();
      const dataUrl = await new Promise((res) => {
        const reader = new FileReader();
        reader.onload = () => res(reader.result);
        reader.readAsDataURL(file);
      });
      state.pendingPhotos.push({ id, blob: file, dataUrl });
    }
    e.target.value = '';
    renderPhotoThumbs();
  });

  renderPhotoThumbs();

  document.getElementById('btn-save').addEventListener('click', saveEntry);
}

function renderPhotoThumbs() {
  const wrap = document.getElementById('photo-thumbs');
  if (!wrap) return;
  wrap.innerHTML = state.pendingPhotos.map((p, i) => `
    <div class="thumb-wrap">
      <img src="${p.dataUrl}">
      <button class="remove-x" data-i="${i}">×</button>
    </div>
  `).join('');
  wrap.querySelectorAll('.remove-x').forEach((btn) => {
    btn.addEventListener('click', () => {
      state.pendingPhotos.splice(Number(btn.dataset.i), 1);
      renderPhotoThumbs();
    });
  });
}

async function saveEntry() {
  const date = document.getElementById('f-date').value || todayStr();
  const paddockSel = document.getElementById('f-paddock');
  const paddockId = paddockSel ? paddockSel.value : null;

  if (!paddockId) {
    toast('Add a paddock first');
    return;
  }

  const notes = document.getElementById('f-notes').value.trim();
  const entry = {
    id: DB.genId(),
    type: state.entryType,
    date,
    paddockId,
    notes,
    photoIds: state.pendingPhotos.map((p) => p.id),
    createdAt: Date.now(),
  };

  if (state.entryType === 'grazing') {
    const groupSel = document.getElementById('f-group');
    if (!groupSel) {
      toast('Add a livestock group first');
      return;
    }
    entry.livestockGroupId = groupSel.value;
    entry.moveType = document.getElementById('f-move').value;
  }

  if (state.entryType === 'input') {
    entry.inputType = document.getElementById('f-input-type').value.trim();
    entry.quantity = document.getElementById('f-quantity').value.trim();
    entry.source = document.getElementById('f-source').value.trim();
  }

  if (state.entryType === 'cover_crop') {
    entry.crop = document.getElementById('f-crop').value.trim();
    entry.cropAction = document.getElementById('f-crop-action').value;
    entry.cropRate = document.getElementById('f-crop-rate').value.trim();
  }

  for (const photo of state.pendingPhotos) {
    await DB.put('photos', { id: photo.id, blob: photo.blob, entryId: entry.id, createdAt: Date.now() });
  }
  await DB.put('entries', entry);

  state.pendingPhotos = [];
  toast('Entry saved ✓');
  renderLog();
}

// ---------- Timeline ----------

async function renderTimeline() {
  const paddockOptions = state.paddocks.map((p) => `<option value="${p.id}">${escapeHtml(p.name)}</option>`).join('');
  root.innerHTML = `
    <h2>Timeline</h2>
    <div class="filter-row">
      <select id="filt-paddock">
        <option value="">All paddocks</option>
        ${paddockOptions}
      </select>
      <select id="filt-type">
        <option value="">All types</option>
        <option value="note">Notes</option>
        <option value="grazing">Grazing</option>
        <option value="input">Soil/Input</option>
        <option value="cover_crop">Cover Crop</option>
      </select>
    </div>
    <div class="card" id="entry-list"><div class="empty-state">Loading…</div></div>
  `;

  document.getElementById('filt-paddock').value = state.timelineFilter.paddockId;
  document.getElementById('filt-type').value = state.timelineFilter.type;

  document.getElementById('filt-paddock').addEventListener('change', (e) => {
    state.timelineFilter.paddockId = e.target.value;
    renderEntryList();
  });
  document.getElementById('filt-type').addEventListener('change', (e) => {
    state.timelineFilter.type = e.target.value;
    renderEntryList();
  });

  await renderEntryList();
}

async function renderEntryList() {
  const listEl = document.getElementById('entry-list');
  let entries = await DB.getAll('entries');
  entries.sort((a, b) => (b.date + b.createdAt).localeCompare(a.date + a.createdAt));

  if (state.timelineFilter.paddockId) {
    entries = entries.filter((e) => e.paddockId === state.timelineFilter.paddockId);
  }
  if (state.timelineFilter.type) {
    entries = entries.filter((e) => e.type === state.timelineFilter.type);
  }

  if (!entries.length) {
    listEl.innerHTML = `<div class="empty-state">No entries yet. Log something from the Log tab.</div>`;
    return;
  }

  listEl.innerHTML = entries.map((e) => {
    const [cls, label] = ENTRY_BADGES[e.type];
    const detailText = entryDetailText(e);
    const detail = detailText ? `<div class="entry-body"><strong>${escapeHtml(detailText)}</strong></div>` : '';
    return `
      <div class="entry" data-id="${e.id}">
        <div class="entry-meta">
          <span><span class="entry-badge ${cls}">${label}</span>${escapeHtml(paddockName(e.paddockId))}</span>
          <span>${formatDate(e.date)}</span>
        </div>
        ${detail}
        ${e.notes ? `<div class="entry-body">${escapeHtml(e.notes)}</div>` : ''}
        <div class="entry-photos" data-photos="${(e.photoIds || []).join(',')}"></div>
        <div class="entry-actions">
          <button class="btn danger small" data-del="${e.id}">Delete</button>
        </div>
      </div>
    `;
  }).join('');

  for (const e of entries) {
    if (e.photoIds && e.photoIds.length) {
      const photoDiv = listEl.querySelector(`.entry[data-id="${e.id}"] .entry-photos`);
      for (const pid of e.photoIds) {
        const photo = await DB.get('photos', pid);
        if (photo) {
          const url = URL.createObjectURL(photo.blob);
          state.objectUrls.push(url);
          const img = document.createElement('img');
          img.src = url;
          photoDiv.appendChild(img);
        }
      }
    }
  }

  listEl.querySelectorAll('[data-del]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      if (!confirm('Delete this entry?')) return;
      const id = btn.dataset.del;
      const entry = entries.find((e) => e.id === id);
      if (entry && entry.photoIds) {
        for (const pid of entry.photoIds) await DB.delete('photos', pid);
      }
      await DB.delete('entries', id);
      toast('Entry deleted');
      renderEntryList();
    });
  });
}

// ---------- Dashboard (paddock rest tracking) ----------

async function renderDashboard() {
  const entries = await DB.getAll('entries');
  const grazingByPaddock = {};
  entries.filter((e) => e.type === 'grazing').forEach((e) => {
    const list = grazingByPaddock[e.paddockId] || (grazingByPaddock[e.paddockId] = []);
    list.push(e);
  });
  Object.values(grazingByPaddock).forEach((list) => list.sort((a, b) => b.date.localeCompare(a.date)));

  if (!state.paddocks.length) {
    root.innerHTML = `<h2>Paddocks</h2><div class="empty-state">No paddocks yet. Add one from the Log tab or Manage tab.</div>`;
    return;
  }

  root.innerHTML = `
    <h2>Paddocks &amp; Rest Tracking</h2>
    ${state.paddocks.map((p) => {
      const last = (grazingByPaddock[p.id] || [])[0];
      let restHtml = `<div class="paddock-rest rest-none">No grazing logged yet</div>`;
      if (last) {
        const days = daysBetween(last.date);
        const statusWord = last.moveType === 'in' ? 'currently grazing (moved in' : 'resting since moved out';
        const cls = last.moveType === 'out' ? (days >= 30 ? 'rest-ok' : 'rest-warn') : 'rest-warn';
        restHtml = `<div class="paddock-rest ${cls}">${last.moveType === 'in' ? '🐄 Grazing since' : '🌱 Resting —'} ${formatDate(last.date)} (${days} day${days === 1 ? '' : 's'} ago)${groupName(last.livestockGroupId) !== '(unknown group)' ? ' · ' + groupName(last.livestockGroupId) : ''}</div>`;
      }
      return `
        <div class="card paddock-card">
          <div>
            <div class="paddock-name">${escapeHtml(p.name)}</div>
            ${restHtml}
          </div>
        </div>
      `;
    }).join('')}
  `;
}

// ---------- Manage (paddocks + livestock groups) ----------

function renderManage() {
  root.innerHTML = `
    <h2>Manage</h2>
    <h3>Paddocks</h3>
    ${paddockLimitReached() ? upgradeCard('Add another paddock') : `
      <div class="card">
        <input type="text" id="new-paddock" placeholder="New paddock name…">
        <button class="btn block" id="add-paddock">Add Paddock</button>
      </div>
    `}
    <div class="manage-list" id="paddock-list"></div>

    <h3>Livestock Groups</h3>
    <div class="card">
      <input type="text" id="new-group" placeholder="New livestock group name…">
      <button class="btn block" id="add-group">Add Livestock Group</button>
    </div>
    <div class="manage-list" id="group-list"></div>
  `;

  renderManageLists();

  bindUpgradeCard(root);

  const managePaddockBtn = document.getElementById('add-paddock');
  if (managePaddockBtn) managePaddockBtn.addEventListener('click', async () => {
    const input = document.getElementById('new-paddock');
    const name = input.value.trim();
    if (!name) return;
    if (paddockLimitReached()) {
      toast('Free keeps 1 paddock — unlock for more');
      return renderManage();
    }
    await DB.put('paddocks', { id: DB.genId(), name, createdAt: Date.now() });
    input.value = '';
    await loadRefData();
    renderManageLists();
    toast(`Added "${name}"`);
  });

  document.getElementById('add-group').addEventListener('click', async () => {
    const input = document.getElementById('new-group');
    const name = input.value.trim();
    if (!name) return;
    await DB.put('livestockGroups', { id: DB.genId(), name, createdAt: Date.now() });
    input.value = '';
    await loadRefData();
    renderManageLists();
    toast(`Added "${name}"`);
  });
}

function renderManageLists() {
  const pList = document.getElementById('paddock-list');
  pList.innerHTML = state.paddocks.length
    ? state.paddocks.map((p) => `
        <div class="manage-item">
          <span>${escapeHtml(p.name)}</span>
          <button class="btn danger small" data-del-paddock="${p.id}">Delete</button>
        </div>
      `).join('')
    : `<div class="empty-state">None yet</div>`;

  const gList = document.getElementById('group-list');
  gList.innerHTML = state.livestockGroups.length
    ? state.livestockGroups.map((g) => `
        <div class="manage-item">
          <span>${escapeHtml(g.name)}</span>
          <button class="btn danger small" data-del-group="${g.id}">Delete</button>
        </div>
      `).join('')
    : `<div class="empty-state">None yet</div>`;

  pList.querySelectorAll('[data-del-paddock]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      if (!confirm('Delete this paddock? Existing log entries will keep referencing it by id but it will show as unknown.')) return;
      await DB.delete('paddocks', btn.dataset.delPaddock);
      await loadRefData();
      renderManageLists();
    });
  });
  gList.querySelectorAll('[data-del-group]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      if (!confirm('Delete this livestock group?')) return;
      await DB.delete('livestockGroups', btn.dataset.delGroup);
      await loadRefData();
      renderManageLists();
    });
  });
}

// ---------- Export (audit-ready PDF) ----------

function renderExport() {
  const paddockChecks = state.paddocks.map((p) => `
    <label class="check-chip"><input type="checkbox" class="chk-paddock" value="${p.id}" checked> ${escapeHtml(p.name)}</label>
  `).join('');

  const typeDefs = [
    ['note', '📝 Notes'],
    ['grazing', '🐄 Grazing'],
    ['input', '🌾 Soil/Input'],
    ['cover_crop', '🌿 Cover Crop'],
  ];
  const typeChecks = typeDefs.map(([val, label]) => `
    <label class="check-chip"><input type="checkbox" class="chk-type" value="${val}" checked> ${label}</label>
  `).join('');

  root.innerHTML = `
    <h2>Export Audit Report</h2>
    <div class="card">
      <label>Date range (leave blank for all recorded dates)</label>
      <div class="date-range">
        <div>
          <label style="margin-top:0;">From</label>
          <input type="date" id="exp-from">
        </div>
        <div>
          <label style="margin-top:0;">To</label>
          <input type="date" id="exp-to" value="${todayStr()}">
        </div>
      </div>

      <label>Paddocks</label>
      ${state.paddocks.length ? `<div class="check-grid">${paddockChecks}</div>` : `<div class="entry-body">No paddocks yet — add one from the Log tab.</div>`}

      <label>Entry types</label>
      <div class="check-grid">${typeChecks}</div>

      ${License.canExportPdf(License.isPro())
        ? `<button class="btn block" id="btn-generate">Generate Audit-Ready PDF</button>`
        : `<div class="locked-inline">🔒 The audit PDF is part of the $29 unlock.</div>`}
    </div>
    ${License.canExportPdf(License.isPro()) ? '' : upgradeCard('Export your audit PDF')}
    <div class="card">
      <div class="entry-body" style="font-size:0.85rem;color:var(--text-dim);">
        Builds a printable report grouped by paddock, in chronological order — grazing moves, input applications (with source), cover crop plantings/terminations, notes, and attached photos. Your browser's print dialog opens next; choose "Save as PDF" as the destination.
      </div>
    </div>
  `;

  bindUpgradeCard(root);
  const genBtn = document.getElementById('btn-generate');
  if (genBtn) genBtn.addEventListener('click', generateReport);
}

async function generateReport() {
  // Second, authoritative check. The button is hidden for free users, but a
  // hidden button is a UI state, not a gate -- this is the line that decides.
  if (!License.canExportPdf(License.isPro())) {
    toast('The audit PDF needs the $29 unlock');
    return switchTab('unlock');
  }
  const from = document.getElementById('exp-from').value;
  const to = document.getElementById('exp-to').value;
  const paddockIds = Array.from(document.querySelectorAll('.chk-paddock:checked')).map((c) => c.value);
  const types = Array.from(document.querySelectorAll('.chk-type:checked')).map((c) => c.value);

  if (!paddockIds.length || !types.length) {
    toast('Select at least one paddock and one entry type');
    return;
  }

  let entries = await DB.getAll('entries');
  entries = entries.filter((e) => paddockIds.includes(e.paddockId) && types.includes(e.type));
  if (from) entries = entries.filter((e) => e.date >= from);
  if (to) entries = entries.filter((e) => e.date <= to);

  if (!entries.length) {
    toast('No entries match this range');
    return;
  }

  state.reportObjectUrls.forEach((u) => URL.revokeObjectURL(u));
  state.reportObjectUrls = [];

  const byPaddock = {};
  entries.forEach((e) => {
    (byPaddock[e.paddockId] || (byPaddock[e.paddockId] = [])).push(e);
  });
  const orderedPaddockIds = state.paddocks.map((p) => p.id).filter((id) => byPaddock[id]);

  const totalCounts = { note: 0, grazing: 0, input: 0, cover_crop: 0 };
  entries.forEach((e) => totalCounts[e.type]++);

  const rangeLabel = from && to ? `${formatDate(from)} – ${formatDate(to)}`
    : from ? `${formatDate(from)} – present`
    : to ? `through ${formatDate(to)}`
    : 'All recorded dates';

  let html = `
    <h1>Regen Farm Field Log &mdash; Audit Report</h1>
    <div class="report-meta">
      Reporting period: ${rangeLabel}<br>
      Paddocks covered: ${orderedPaddockIds.map((id) => escapeHtml(paddockName(id))).join(', ')}<br>
      Generated: ${new Date().toLocaleString()}<br>
      Summary: ${totalCounts.grazing} grazing event(s), ${totalCounts.input} input application(s), ${totalCounts.cover_crop} cover crop event(s), ${totalCounts.note} general note(s)
    </div>
  `;

  for (const pid of orderedPaddockIds) {
    const list = byPaddock[pid].slice().sort((a, b) => (a.date + a.createdAt).localeCompare(b.date + b.createdAt));
    html += `<h2 class="paddock-heading">${escapeHtml(paddockName(pid))}</h2>`;
    for (const e of list) {
      const [, label] = ENTRY_BADGES[e.type];
      const badgeText = label.replace(/^\S+\s/, '');
      const detailText = entryDetailText(e);
      html += `
        <div class="r-entry">
          <div class="r-meta"><span class="r-badge">${badgeText}</span>${formatDate(e.date)}</div>
          ${detailText ? `<div><strong>${escapeHtml(detailText)}</strong></div>` : ''}
          ${e.notes ? `<div>${escapeHtml(e.notes)}</div>` : ''}
          <div class="r-photos" data-entry="${e.id}"></div>
        </div>
      `;
    }
  }

  html += `<div class="report-footer">Generated by Regen Farm Field Log on ${new Date().toLocaleString()}. Entries are recorded directly by the operator at the time of each field activity.</div>`;

  const reportEl = document.getElementById('print-report');
  reportEl.innerHTML = html;

  for (const e of entries) {
    if (!e.photoIds || !e.photoIds.length) continue;
    const photoDiv = reportEl.querySelector(`.r-photos[data-entry="${e.id}"]`);
    if (!photoDiv) continue;
    for (const pid of e.photoIds) {
      const photo = await DB.get('photos', pid);
      if (photo) {
        const url = URL.createObjectURL(photo.blob);
        state.reportObjectUrls.push(url);
        const img = document.createElement('img');
        img.src = url;
        photoDiv.appendChild(img);
      }
    }
  }

  document.body.classList.add('printing');
  window.print();
}

window.addEventListener('afterprint', () => {
  document.body.classList.remove('printing');
});

// ---------- Unlock ----------

function renderUnlock() {
  const info = License.info();

  if (info) {
    root.innerHTML = `
      <h2>Unlocked</h2>
      <div class="card">
        <div class="upsell-title">✅ You have the full version</div>
        <div class="entry-body">Unlimited paddocks and the audit PDF are on.
        No subscription — you own this.</div>
        <div class="entry-body" style="font-size:0.8rem;color:var(--text-dim);">
          Unlocked ${escapeHtml((info.activatedAt || '').slice(0, 10))}
        </div>
      </div>
    `;
    return;
  }

  root.innerHTML = `
    <h2>Unlock the Full Log</h2>
    <div class="card">
      <div class="entry-body"><strong>Free</strong> gives you ${License.FREE_PADDOCK_LIMIT} paddock,
      every entry type, photos, and the timeline. It stays free.</div>
      <div class="entry-body"><strong>$29, one time</strong> adds every paddock you farm
      and the audit-ready PDF your certifier asks for.</div>
      <a class="btn block" href="${License.PRODUCT_URL}" target="_blank" rel="noopener">Buy for $29</a>
    </div>

    <div class="card">
      <label>Already bought? Paste your code</label>
      <input type="text" id="lic-key" placeholder="Code from your receipt" autocapitalize="characters" autocomplete="off">
      <button class="btn block" id="btn-activate">Unlock</button>
      <div id="lic-msg" class="entry-body" style="margin-top:8px;"></div>
      <div class="entry-body" style="font-size:0.8rem;color:var(--text-dim);">
        Checked once over the internet, then remembered on this device — the app
        keeps working with no signal.
      </div>
    </div>
  `;

  const btn = document.getElementById('btn-activate');
  const msg = document.getElementById('lic-msg');
  btn.addEventListener('click', async () => {
    btn.disabled = true;
    msg.textContent = 'Checking…';
    const res = await License.activate(document.getElementById('lic-key').value);
    msg.textContent = res.message;
    btn.disabled = false;
    if (res.ok) {
      toast('Unlocked ✓');
      render();
    }
  });
}

// ---------- Init ----------

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('sw.js').catch(() => {});
  });
}

render();
