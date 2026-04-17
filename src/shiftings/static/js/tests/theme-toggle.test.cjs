const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

const scriptPath = path.resolve(__dirname, '..', 'theme-toggle.js');
const scriptContent = fs.readFileSync(scriptPath, 'utf8');

function makeClassList() {
  const classes = new Set();
  return {
    toggle(className, enabled) {
      if (enabled) {
        classes.add(className);
      } else {
        classes.delete(className);
      }
    },
    contains(className) {
      return classes.has(className);
    },
  };
}

function makeOption(mode, formId) {
  const listeners = {};
  return {
    dataset: {
      theme: mode,
      themeForm: formId,
    },
    classList: makeClassList(),
    addEventListener(eventName, callback) {
      listeners[eventName] = callback;
    },
    click() {
      const event = {
        defaultPrevented: false,
        preventDefault() {
          this.defaultPrevented = true;
        },
      };
      listeners.click(event);
      return event;
    },
  };
}

function setupEnvironment({ userTheme = 'auto', storageTheme = null, xMatch = false, lightMatch = false } = {}) {
  const root = { dataset: { userTheme } };
  const options = [
    makeOption('light', 'theme-light-form'),
    makeOption('dark', 'theme-dark-form'),
    makeOption('auto', 'theme-auto-form'),
  ];
  const forms = {
    'theme-light-form': { submitted: false, submit() { this.submitted = true; } },
    'theme-dark-form': { submitted: false, submit() { this.submitted = true; } },
    'theme-auto-form': { submitted: false, submit() { this.submitted = true; } },
  };

  const storage = new Map();
  if (storageTheme !== null) {
    storage.set('shiftings-theme-preference', storageTheme);
  }

  const listenersByQuery = new Map();
  const queryMatch = new Map([
    ['(prefers-color-scheme: x)', xMatch],
    ['(prefers-color-scheme: light)', lightMatch],
  ]);

  const localStorage = {
    getItem(key) {
      return storage.has(key) ? storage.get(key) : null;
    },
    setItem(key, value) {
      storage.set(key, value);
    },
  };

  const document = {
    documentElement: root,
    querySelectorAll(selector) {
      if (selector === '.js-theme-option') {
        return options;
      }
      return [];
    },
    getElementById(id) {
      return forms[id] || null;
    },
  };

  const windowObject = {
    matchMedia(query) {
      const listeners = [];
      listenersByQuery.set(query, listeners);
      return {
        get matches() {
          return Boolean(queryMatch.get(query));
        },
        addEventListener(eventName, callback) {
          if (eventName === 'change') {
            listeners.push(callback);
          }
        },
      };
    },
  };

  global.document = document;
  global.window = windowObject;
  global.localStorage = localStorage;

  return {
    options,
    forms,
    root,
    storage,
    queryMatch,
    listenersByQuery,
  };
}

function teardownEnvironment() {
  delete global.document;
  delete global.window;
  delete global.localStorage;
}

function runThemeToggleScript() {
  // eslint-disable-next-line no-new-func
  new Function(scriptContent)();
}

test('prefers localStorage theme over account theme', () => {
  const env = setupEnvironment({ userTheme: 'dark', storageTheme: 'light' });
  runThemeToggleScript();

  assert.equal(env.root.dataset.themeMode, 'light');
  assert.equal(env.root.dataset.bsTheme, 'light');
  assert.equal(env.options[0].classList.contains('active'), true);
  assert.equal(env.options[1].classList.contains('active'), false);
  assert.equal(env.options[2].classList.contains('active'), false);

  teardownEnvironment();
});

test('falls back to account theme when no localStorage value exists', () => {
  const env = setupEnvironment({ userTheme: 'dark', storageTheme: null });
  runThemeToggleScript();

  assert.equal(env.root.dataset.themeMode, 'dark');
  assert.equal(env.root.dataset.bsTheme, 'dark');

  teardownEnvironment();
});

test('clicking option saves preference, updates active entry, and submits linked form', () => {
  const env = setupEnvironment({ userTheme: 'auto', storageTheme: null, xMatch: true });
  runThemeToggleScript();

  const autoClickEvent = env.options[2].click();

  assert.equal(autoClickEvent.defaultPrevented, true);
  assert.equal(env.storage.get('shiftings-theme-preference'), 'auto');
  assert.equal(env.root.dataset.themeMode, 'auto');
  assert.equal(env.root.dataset.bsTheme, 'light');
  assert.equal(env.forms['theme-auto-form'].submitted, true);
  assert.equal(env.options[2].classList.contains('active'), true);
  assert.equal(env.options[0].classList.contains('active'), false);
  assert.equal(env.options[1].classList.contains('active'), false);

  teardownEnvironment();
});

test('system theme change re-applies theme only in auto mode', () => {
  const env = setupEnvironment({ userTheme: 'auto', storageTheme: 'auto', xMatch: false, lightMatch: false });
  runThemeToggleScript();

  const systemListeners = env.listenersByQuery.get('(prefers-color-scheme: light)');
  assert.ok(systemListeners);
  assert.equal(systemListeners.length, 1);

  env.queryMatch.set('(prefers-color-scheme: x)', true);
  env.queryMatch.set('(prefers-color-scheme: light)', true);
  systemListeners[0]();

  assert.equal(env.root.dataset.themeMode, 'auto');
  assert.equal(env.root.dataset.bsTheme, 'light');

  env.options[1].click();
  assert.equal(env.root.dataset.themeMode, 'dark');

  env.queryMatch.set('(prefers-color-scheme: x)', false);
  env.queryMatch.set('(prefers-color-scheme: light)', false);
  systemListeners[0]();

  assert.equal(env.root.dataset.themeMode, 'dark');
  assert.equal(env.root.dataset.bsTheme, 'dark');

  teardownEnvironment();
});
