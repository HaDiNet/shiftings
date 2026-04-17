const assert = require('node:assert/strict');
const path = require('node:path');
const test = require('node:test');

const {
  createDocument,
  createElement,
  installDomGlobals,
  loadScript,
  teardownDomGlobals,
} = require('./dom-harness.cjs');

function setupEnvironment({ userTheme = 'auto', storageTheme = null, xMatch = false, lightMatch = false } = {}) {
  const root = createElement({ tagName: 'HTML', id: 'root', dataset: { userTheme } });
  const lightOption = createElement({ id: 'light-option', tagName: 'A', classNames: ['js-theme-option'], dataset: { theme: 'light', themeForm: 'theme-light-form' } });
  const darkOption = createElement({ id: 'dark-option', tagName: 'A', classNames: ['js-theme-option'], dataset: { theme: 'dark', themeForm: 'theme-dark-form' } });
  const autoOption = createElement({ id: 'auto-option', tagName: 'A', classNames: ['js-theme-option'], dataset: { theme: 'auto', themeForm: 'theme-auto-form' } });
  const lightForm = createElement({ id: 'theme-light-form', tagName: 'FORM' });
  const darkForm = createElement({ id: 'theme-dark-form', tagName: 'FORM' });
  const autoForm = createElement({ id: 'theme-auto-form', tagName: 'FORM' });

  lightForm.submit = function submit() {
    this.submitted = true;
  };
  darkForm.submit = function submit() {
    this.submitted = true;
  };
  autoForm.submit = function submit() {
    this.submitted = true;
  };

  root.appendChild(lightOption);
  root.appendChild(darkOption);
  root.appendChild(autoOption);
  root.appendChild(lightForm);
  root.appendChild(darkForm);
  root.appendChild(autoForm);

  const document = createDocument({ root });
  const storage = new Map();
  if (storageTheme !== null) {
    storage.set('shiftings-theme-preference', storageTheme);
  }

  const queryMatch = new Map([
    ['(prefers-color-scheme: x)', xMatch],
    ['(prefers-color-scheme: light)', lightMatch],
  ]);
  const listenersByQuery = new Map();

  installDomGlobals(document, {
    window: {
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
    },
  });
  global.localStorage = {
    getItem(key) {
      return storage.has(key) ? storage.get(key) : null;
    },
    setItem(key, value) {
      storage.set(key, value);
    },
  };

  return {
    document,
    root,
    lightOption,
    darkOption,
    autoOption,
    lightForm,
    darkForm,
    autoForm,
    storage,
    queryMatch,
    listenersByQuery,
  };
}

function teardownEnvironment() {
  teardownDomGlobals();
}

function runThemeToggleScript() {
  loadScript(path.resolve(__dirname, '..', 'theme-toggle.js'));
}

test('prefers localStorage theme over account theme', () => {
  const env = setupEnvironment({ userTheme: 'dark', storageTheme: 'light' });
  runThemeToggleScript();

  assert.equal(env.root.dataset.themeMode, 'light');
  assert.equal(env.root.dataset.bsTheme, 'light');
  assert.equal(env.lightOption.classList.contains('active'), true);
  assert.equal(env.darkOption.classList.contains('active'), false);
  assert.equal(env.autoOption.classList.contains('active'), false);

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

  const autoClickEvent = {
    defaultPrevented: false,
    preventDefault() {
      this.defaultPrevented = true;
    },
    type: 'click',
  };
  env.autoOption.dispatchEvent(autoClickEvent);

  assert.equal(autoClickEvent.defaultPrevented, true);
  assert.equal(env.storage.get('shiftings-theme-preference'), 'auto');
  assert.equal(env.root.dataset.themeMode, 'auto');
  assert.equal(env.root.dataset.bsTheme, 'light');
  assert.equal(env.autoForm.submitted, true);
  assert.equal(env.autoOption.classList.contains('active'), true);
  assert.equal(env.lightOption.classList.contains('active'), false);
  assert.equal(env.darkOption.classList.contains('active'), false);

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

  env.darkOption.dispatchEvent({ type: 'click', preventDefault() {} });
  assert.equal(env.root.dataset.themeMode, 'dark');

  env.queryMatch.set('(prefers-color-scheme: x)', false);
  env.queryMatch.set('(prefers-color-scheme: light)', false);
  systemListeners[0]();

  assert.equal(env.root.dataset.themeMode, 'dark');
  assert.equal(env.root.dataset.bsTheme, 'dark');

  teardownEnvironment();
});
