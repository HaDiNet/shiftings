const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

const { createElement } = require('./dom-harness.cjs');

const scriptPath = path.resolve(__dirname, '..', 'save_and_restore.js');
const scriptContent = fs.readFileSync(scriptPath, 'utf8');

function loadSaveAndRestore() {
  // eslint-disable-next-line no-new-func
  return new Function(`${scriptContent}\nreturn saveAndRestore;`)();
}

function makeComponent(tagName, id, value) {
  const wrapper = createElement({ id: `${id}-wrapper` });
  const component = createElement({ tagName, id, value, innerText: value });
  if (tagName === 'SELECT') {
    component.selectedIndex = value;
  }
  wrapper.appendChild(component);
  return component;
}

test('save hides and clears components, restore shows and restores values', () => {
  const saveAndRestore = loadSaveAndRestore();

  const input = makeComponent('INPUT', 'input-id', 'abc');
  const select = makeComponent('SELECT', 'select-id', 2);
  const text = makeComponent('SPAN', 'text-id', 'hello');

  saveAndRestore.save(true, true, input, select, text);

  assert.equal(input.parentNode.classList.contains('d-none'), true);
  assert.equal(select.parentNode.classList.contains('d-none'), true);
  assert.equal(text.parentNode.classList.contains('d-none'), true);

  assert.equal(input.value, '');
  assert.equal(select.selectedIndex, 0);
  assert.equal(text.innerText, '');

  saveAndRestore.restore(true, input, select, text);

  assert.equal(input.parentNode.classList.contains('d-none'), false);
  assert.equal(select.parentNode.classList.contains('d-none'), false);
  assert.equal(text.parentNode.classList.contains('d-none'), false);

  assert.equal(input.value, 'abc');
  assert.equal(select.selectedIndex, 2);
  assert.equal(text.innerText, 'hello');
});

test('save keeps previously stored non-empty value when later value is empty', () => {
  const saveAndRestore = loadSaveAndRestore();

  const input = makeComponent('INPUT', 'persist-id', 'first');
  saveAndRestore.save(false, false, input);

  input.value = '';
  saveAndRestore.save(false, false, input);

  input.value = 'changed';
  saveAndRestore.restore(false, input);

  assert.equal(input.value, 'first');
});

test('restore only applies once for stored values', () => {
  const saveAndRestore = loadSaveAndRestore();

  const input = makeComponent('INPUT', 'once-id', 'value-1');
  saveAndRestore.save(false, false, input);

  input.value = 'value-2';
  saveAndRestore.restore(false, input);
  assert.equal(input.value, 'value-1');

  input.value = 'value-3';
  saveAndRestore.restore(false, input);
  assert.equal(input.value, 'value-3');
});
