const fs = require('node:fs');
const vm = require('node:vm');

function createClassList(initialClasses = []) {
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
    toArray() {
      return Array.from(classes);
    },
  };
}

function matchesSelector(element, selector) {
  const attributeMatch = selector.match(/^\[([^=\]]+)=([^\]]+)\]$/);
  if (attributeMatch) {
    const attributeName = attributeMatch[1];
    const attributeValue = attributeMatch[2].replace(/^['"]|['"]$/g, '');
    const attribute = element.attributes?.[attributeName];
    return element[attributeName] === attributeValue || attribute === attributeValue || attribute?.nodeValue === attributeValue;
  }
  return false;
}

function walk(element, callback) {
  callback(element);
  for (const child of element.children) {
    walk(child, callback);
  }
}

function createElement({
  id = '',
  tagName = 'DIV',
  classNames = [],
  dataset = {},
  value = '',
  innerText = '',
  textContent = '',
  name = '',
  type = '',
  attributes = {},
} = {}) {
  const listeners = {};
  const element = {
    id,
    tagName: String(tagName).toUpperCase(),
    classList: createClassList(classNames),
    dataset,
    children: [],
    parentNode: null,
    parentElement: null,
    style: {},
    value,
    innerText,
    textContent,
    name,
    type,
    attributes,
    reportValidity() {
      return true;
    },
    focusCalled: false,
    focus() {
      element.focusCalled = true;
    },
    addEventListener(eventName, callback) {
      listeners[eventName] = callback;
    },
    dispatchEvent(event) {
      const dispatchedEvent = event || { type: undefined };
      if (!dispatchedEvent.target) {
        dispatchedEvent.target = element;
      }
      dispatchedEvent.currentTarget = element;
      if (listeners[dispatchedEvent.type]) {
        listeners[dispatchedEvent.type](dispatchedEvent);
      }
      if (dispatchedEvent.bubbles && global.document && global.document !== element.ownerDocument) {
        global.document.dispatchEvent(dispatchedEvent);
      }
      return true;
    },
    appendChild(child) {
      child.parentNode = element;
      child.parentElement = element;
      child.ownerDocument = element.ownerDocument;
      element.children.push(child);
      if (global.document && typeof global.document._registerTree === 'function') {
        global.document._registerTree(child);
      }
      return child;
    },
    getElementsByClassName(className) {
      const result = [];
      walk(element, (node) => {
        if (node.classList.contains(className)) {
          result.push(node);
        }
      });
      return result;
    },
    getElementsByName(searchName) {
      const result = [];
      walk(element, (node) => {
        if (node.name === searchName) {
          result.push(node);
        }
      });
      return result;
    },
    querySelectorAll(selector) {
      const result = [];
      if (selector.startsWith('.')) {
        const className = selector.slice(1);
        walk(element, (node) => {
          if (node.classList.contains(className)) {
            result.push(node);
          }
        });
      }
      return result;
    },
    querySelector(selector) {
      let found = null;
      walk(element, (node) => {
        if (!found && matchesSelector(node, selector)) {
          found = node;
        }
      });
      return found;
    },
    getAttribute(attributeName) {
      const attribute = attributes[attributeName];
      return attribute?.nodeValue ?? attribute;
    },
    setAttribute(attributeName, attributeValue) {
      attributes[attributeName] = { nodeValue: attributeValue };
    },
  };
  return element;
}

function createDocument({ root = createElement({ tagName: 'HTML', id: 'root' }), locationHref = 'about:blank' } = {}) {
  const elementsById = new Map();
  const listeners = {};
  const document = {
    documentElement: root,
    location: { href: locationHref },
    addEventListener(eventName, callback) {
      listeners[eventName] = callback;
    },
    dispatchEvent(event) {
      const dispatchedEvent = typeof event === 'string' ? { type: event } : event;
      if (!dispatchedEvent.target) {
        dispatchedEvent.target = document;
      }
      dispatchedEvent.currentTarget = document;
      if (listeners[dispatchedEvent.type]) {
        listeners[dispatchedEvent.type](dispatchedEvent);
      }
      return true;
    },
    getElementById(id) {
      return elementsById.get(id) || null;
    },
    getElementsByClassName(className) {
      const result = [];
      walk(root, (node) => {
        if (node.classList.contains(className)) {
          result.push(node);
        }
      });
      return result;
    },
    getElementsByName(searchName) {
      const result = [];
      walk(root, (node) => {
        if (node.name === searchName) {
          result.push(node);
        }
      });
      return result;
    },
    querySelectorAll(selector) {
      const result = [];
      if (selector.startsWith('.')) {
        const className = selector.slice(1);
        walk(root, (node) => {
          if (node.classList.contains(className)) {
            result.push(node);
          }
        });
      }
      return result;
    },
    createElement(tagName) {
      const element = createElement({ tagName });
      element.ownerDocument = document;
      return element;
    },
    _registerTree(element) {
      walk(element, (node) => {
        node.ownerDocument = document;
        if (node.id) {
          elementsById.set(node.id, node);
        }
      });
    },
  };
  root.ownerDocument = document;
  document._registerTree(root);
  return document;
}

class MockMutationObserver {
  constructor(callback) {
    this.callback = callback;
    this.target = null;
    this.options = null;
    MockMutationObserver.instances.push(this);
  }

  observe(target, options) {
    this.target = target;
    this.options = options;
  }

  trigger(records = []) {
    this.callback(records, this);
  }
}

MockMutationObserver.instances = [];

class MockCustomEvent {
  constructor(type, init = {}) {
    this.type = type;
    Object.assign(this, init);
  }
}

function installDomGlobals(document, extras = {}) {
  global.document = document;
  global.window = extras.window || {};
  global.CustomEvent = extras.CustomEvent || MockCustomEvent;
  global.MutationObserver = extras.MutationObserver || MockMutationObserver;
  if (extras.saveAndRestore) {
    global.saveAndRestore = extras.saveAndRestore;
  }
  return document;
}

function teardownDomGlobals() {
  delete global.document;
  delete global.window;
  delete global.CustomEvent;
  delete global.MutationObserver;
  delete global.localStorage;
  delete global.saveAndRestore;
}

function loadScript(scriptPath) {
  const scriptContent = fs.readFileSync(scriptPath, 'utf8');
  vm.runInThisContext(scriptContent, { filename: scriptPath });
}

module.exports = {
  MockCustomEvent,
  MockMutationObserver,
  createDocument,
  createElement,
  installDomGlobals,
  loadScript,
  teardownDomGlobals,
};
