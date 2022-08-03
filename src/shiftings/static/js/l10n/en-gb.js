(function (global, factory) {
  typeof exports === 'object' && typeof module !== 'undefined' ? factory(exports) :
  typeof define === 'function' && define.amd ? define(['exports'], factory) :
  (global = typeof globalThis !== 'undefined' ? globalThis : global || self, factory(global['en-gb'] = {}));
}(this, (function (exports) {
  'use strict';

  var fp = typeof window !== 'undefined' && window.flatpickr !== undefined
           ? window.flatpickr
           : {
        l10ns: {},
      };
  var BritishEnglish = {
    firstDayOfWeek: 1,
    time_24hr: true,
  };
  fp.l10ns['en-gb'] = BritishEnglish;
  var enGb = fp.l10ns;

  exports.BritishEnglish = BritishEnglish;
  exports.default = enGb;

  Object.defineProperty(exports, '__esModule', { value: true });

})));