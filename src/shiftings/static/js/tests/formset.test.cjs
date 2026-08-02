const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

const scriptPath = path.resolve(__dirname, '..', 'formset.js');
const scriptContent = fs.readFileSync(scriptPath, 'utf8');

function makeClassList(initialClasses = []) {
  const classes = new Set(initialClasses);
  return {
    add(...classNames) {
      for (const className of classNames) {
        classes.add(className);
      }
    },
    remove(...classNames) {
      for (const className of classNames) {
        classes.delete(className);
      }
    },
    toggle(className, force) {
      if (force === undefined) {
        if (classes.has(className)) {
          classes.delete(className);
          return false;
        }
        classes.add(className);
        return true;
      }
      if (force) {
        classes.add(className);
      } else {
        classes.delete(className);
      }
      return force;
    },
    contains(className) {
      return classes.has(className);
    },
  };
}

function makeElement({ id = '', tagName = 'DIV', classNames = [], innerHTML = '', value = '' } = {}) {
  const listeners = {};
  const element = {
    id,
    tagName,
    classList: makeClassList(classNames),
    innerHTML,
    value,
    parentNode: null,
    children: [],
    style: {},
    addEventListener(eventName, callback) {
      listeners[eventName] = callback;
    },
    click() {
      const callback = listeners.click;
      if (callback) {
        callback({ currentTarget: element });
      }
    },
    appendChild(child) {
      if (child && child.isFragment) {
        for (const node of child.children) {
          element.appendChild(node);
        }
        return child;
      }
      child.parentNode = element;
      child.parentElement = element;
      element.children.push(child);
      if (global.document && typeof global.document._registerTree === 'function') {
        global.document._registerTree(child);
      }
      return child;
    },
    insertAdjacentElement(position, node) {
      if (position === 'beforeend') {
        return element.appendChild(node);
      }
      return null;
    },
    insertBefore(node, referenceNode) {
      const index = element.children.indexOf(referenceNode);
      if (index < 0) {
        return element.appendChild(node);
      }
      node.parentNode = element;
      node.parentElement = element;
      element.children.splice(index, 0, node);
      if (global.document && typeof global.document._registerTree === 'function') {
        global.document._registerTree(node);
      }
      return node;
    },
    insertAdjacentHTML(position, html) {
      if (position !== 'beforeend') {
        return;
      }
      const idMatch = html.match(/id=\"([^\"]+)\"/);
      const id = idMatch ? idMatch[1] : '';
      const checkbox = makeElement({ id, tagName: 'INPUT', classNames: ['d-none'] });
      checkbox.checked = true;
      checkbox.name = html.match(/name=\"([^\"]+)\"/)?.[1] || '';
      element.appendChild(checkbox);
    },
    getElementsByClassName(className) {
      const result = [];
      for (const child of element.children) {
        if (child.classList.contains(className)) {
          result.push(child);
        }
        result.push(...child.getElementsByClassName(className));
      }
      return result;
    },
    querySelector(selector) {
      if (selector === '[type=submit]') {
        for (const child of element.children) {
          if (child.type === 'submit') {
            return child;
          }
          const nested = child.querySelector(selector);
          if (nested) {
            return nested;
          }
        }
      }
      return null;
    },
  };
  return element;
}

function cloneTree(node) {
  const copy = makeElement({
    id: node.id,
    tagName: node.tagName,
    innerHTML: node.innerHTML,
    classNames: [],
    value: node.value,
  });
  for (const className of ['formset-form-remove', 'formset-form-restore', 'border', 'd-none']) {
    if (node.classList.contains(className)) {
      copy.classList.add(className);
    }
  }
  for (const child of node.children) {
    copy.appendChild(cloneTree(child));
  }
  return copy;
}

function makeDocument(elements = []) {
  const elementsById = new Map();
  const domListeners = {};

  const registerTree = (element) => {
    if (element.id) {
      elementsById.set(element.id, element);
    }
    for (const child of element.children) {
      registerTree(child);
    }
  };

  for (const element of elements) {
    registerTree(element);
  }

  return {
    _registerTree: registerTree,
    addEventListener(eventName, callback) {
      domListeners[eventName] = callback;
    },
    dispatch(eventName) {
      const callback = domListeners[eventName];
      if (callback) {
        callback();
      }
    },
    getElementById(id) {
      return elementsById.get(id) || null;
    },
    getElementsByClassName(className) {
      const result = [];
      for (const element of elementsById.values()) {
        if (element.classList.contains(className)) {
          result.push(element);
        }
      }
      return result;
    },
    createElement(tagName) {
      return makeElement({ tagName: String(tagName).toUpperCase() });
    },
  };
}

function loadFormsetScript() {
  // eslint-disable-next-line no-new-func
  new Function(scriptContent)();
}

function setupAddFormEnvironment(maxForms = '1') {
  const root = makeElement({ id: 'root' });
  const form = makeElement({ id: 'formset_form' });
  const insert = makeElement({ id: 'formset_insert' });
  const addLink = makeElement({ id: 'formset_add', tagName: 'A' });
  const total = makeElement({ id: 'id_form-TOTAL_FORMS', tagName: 'INPUT', value: '0' });
  const max = makeElement({ id: 'id_form-MAX_NUM_FORMS', tagName: 'INPUT', value: maxForms });
  const emptyAlert = makeElement({ id: 'empty_alert', classNames: [] });

  root.appendChild(form);
  form.appendChild(addLink);
  form.appendChild(total);
  form.appendChild(max);
  form.appendChild(insert);
  form.appendChild(emptyAlert);

  const template = makeElement({ id: 'formset_template', tagName: 'TEMPLATE' });
  const childContainer = makeElement({ id: 'id_form-__prefix___container', classNames: ['border'] });
  const childRemove = makeElement({ id: 'id_form-__prefix___remove', classNames: ['formset-form-remove'] });
  const childRestore = makeElement({
    id: 'id_form-__prefix___restore',
    classNames: ['formset-form-restore', 'd-none'],
  });

  template.content = {
    cloneNode() {
      return {
        isFragment: true,
        children: [cloneTree(childContainer), cloneTree(childRemove), cloneTree(childRestore)],
      };
    },
  };

  const document = makeDocument([root, form, addLink, insert, total, max, emptyAlert, template]);
  global.document = document;

  return { document, insert, total, emptyAlert };
}

function setupRemoveRestoreEnvironment() {
  const form = makeElement({ id: 'id_form-0_container', classNames: ['border'] });
  const innerBorder = makeElement({ id: 'id_form-0_inner', classNames: ['border'] });
  const remove = makeElement({ id: 'id_form-0_remove', classNames: ['formset-form-remove'] });
  const restore = makeElement({ id: 'id_form-0_restore', classNames: ['formset-form-restore', 'd-none'] });

  form.appendChild(innerBorder);
  form.appendChild(remove);
  form.appendChild(restore);

  const total = makeElement({ id: 'id_form-TOTAL_FORMS', tagName: 'INPUT', value: '1' });
  const max = makeElement({ id: 'id_form-MAX_NUM_FORMS', tagName: 'INPUT', value: '10' });
  const template = makeElement({ id: 'formset_template', tagName: 'TEMPLATE' });
  template.content = { cloneNode: () => ({ isFragment: true, children: [] }) };

  const holder = makeElement({ id: 'holder' });
  holder.appendChild(total);
  holder.appendChild(max);
  holder.appendChild(form);

  const document = makeDocument([holder, total, max, form, innerBorder, remove, restore, template]);
  global.document = document;

  return { document, form, innerBorder, remove, restore };
}

function teardown() {
  delete global.document;
}

test('adds new form, updates total, and hides add button at max', () => {
  const env = setupAddFormEnvironment('1');
  loadFormsetScript();
  env.document.dispatch('DOMContentLoaded');

  const addLink = env.document.getElementById('formset_add');
  assert.ok(addLink);

  addLink.click();

  assert.equal(env.emptyAlert.classList.contains('d-none'), true);
  assert.equal(String(env.total.value), '1');
  assert.equal(addLink.classList.contains('d-none'), true);
  assert.ok(env.document.getElementById('id_form-0_container'));
  assert.ok(env.document.getElementById('id_form-0_remove'));
  assert.ok(env.document.getElementById('id_form-0_restore'));

  teardown();
});

test('remove and restore toggles delete checkbox and visual state', () => {
  const env = setupRemoveRestoreEnvironment();
  loadFormsetScript();
  env.document.dispatch('DOMContentLoaded');

  env.remove.click();

  const deleteElement = env.document.getElementById('id_form-0-DELETE');
  assert.ok(deleteElement);
  assert.equal(deleteElement.checked, true);
  assert.equal(env.remove.classList.contains('d-none'), true);
  assert.equal(env.restore.classList.contains('d-none'), false);
  assert.equal(env.form.classList.contains('border-danger'), true);
  assert.equal(env.innerBorder.classList.contains('border-danger'), true);
  assert.equal(env.form.style.opacity, '.5');

  env.restore.click();

  assert.equal(deleteElement.checked, false);
  assert.equal(env.remove.classList.contains('d-none'), false);
  assert.equal(env.restore.classList.contains('d-none'), true);
  assert.equal(env.form.classList.contains('border-danger'), false);
  assert.equal(env.innerBorder.classList.contains('border-danger'), false);
  assert.equal(env.form.style.opacity, '1');

  teardown();
});
