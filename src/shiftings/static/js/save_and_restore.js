'use strict';
const saveAndRestore = {};

(function () {
  const tagToAttrMap = {
    'SELECT': { name: 'selectedIndex', empty_value: 0 },
    'INPUT': { name: 'value', empty_value: '' },
  };
  const defaultAttr = { name: 'innerText', empty_value: '' };
  const hideClass = 'd-none';

  let store = {};

  saveAndRestore.save = function save(hide, clear, ...components) {
    for (let component of components) {
      if (hide) {
        component.parentNode.classList.add(hideClass);
      }
      let attr = tagToAttrMap[component.tagName] || defaultAttr;
      if (!(component.id in store) || component[attr.name] !== attr.empty_value) {
        store[component.id] = component[attr.name];
      }
      if (clear) {
        component[attr.name] = attr.empty_value;
      }
    }
  };

  saveAndRestore.restore = function restore(show, ...components) {
    for (let component of components) {
      if (show) {
        component.parentNode.classList.remove(hideClass);
      }
      let attr = tagToAttrMap[component.tagName] || defaultAttr;
      if (component.id in store) {
        component[attr.name] = store[component.id];
        delete store[component.id];
      }
    }
  };
})();