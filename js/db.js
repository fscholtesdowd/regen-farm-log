const DB_NAME = 'regenFarmLog';
const DB_VERSION = 1;

let dbPromise = null;

function openDb() {
  if (dbPromise) return dbPromise;
  dbPromise = new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION);
    req.onupgradeneeded = (e) => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains('paddocks')) {
        db.createObjectStore('paddocks', { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains('livestockGroups')) {
        db.createObjectStore('livestockGroups', { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains('entries')) {
        const entries = db.createObjectStore('entries', { keyPath: 'id' });
        entries.createIndex('byDate', 'date');
        entries.createIndex('byPaddock', 'paddockId');
        entries.createIndex('byType', 'type');
      }
      if (!db.objectStoreNames.contains('photos')) {
        db.createObjectStore('photos', { keyPath: 'id' });
      }
    };
    req.onsuccess = (e) => resolve(e.target.result);
    req.onerror = (e) => reject(e.target.error);
  });
  return dbPromise;
}

function tx(storeName, mode) {
  return openDb().then((db) => db.transaction(storeName, mode).objectStore(storeName));
}

function genId() {
  return Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 9);
}

function reqToPromise(req) {
  return new Promise((resolve, reject) => {
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

const DB = {
  genId,

  async put(storeName, obj) {
    const store = await tx(storeName, 'readwrite');
    return reqToPromise(store.put(obj));
  },

  async get(storeName, id) {
    const store = await tx(storeName, 'readonly');
    return reqToPromise(store.get(id));
  },

  async delete(storeName, id) {
    const store = await tx(storeName, 'readwrite');
    return reqToPromise(store.delete(id));
  },

  async getAll(storeName) {
    const store = await tx(storeName, 'readonly');
    return reqToPromise(store.getAll());
  },

  async getAllByIndex(storeName, indexName, value) {
    const store = await tx(storeName, 'readonly');
    return reqToPromise(store.index(indexName).getAll(value));
  },
};

window.DB = DB;
