(() => {
  const STORAGE_KEY = 'shiftings-theme-preference';
  const root = document.documentElement;

  const resolveTheme = (mode) => {
    if (mode === 'auto') {
      if (!window.matchMedia) {
        return 'dark';
      }
      return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    }
    return mode;
  };

  const applyTheme = (mode) => {
    root.dataset.themeMode = mode;
    root.dataset.bsTheme = resolveTheme(mode);
  };

  const saveTheme = (mode) => {
    localStorage.setItem(STORAGE_KEY, mode);
    applyTheme(mode);
  };

  const updateActiveEntry = (mode) => {
    const entries = document.querySelectorAll('.js-theme-option');
    entries.forEach((entry) => {
      entry.classList.toggle('active', entry.dataset.theme === mode);
    });
  };

  const storageTheme = localStorage.getItem(STORAGE_KEY);
  const hasStorageTheme = storageTheme !== null;
  const accountTheme = root.dataset.userTheme || 'auto';
  const preferredTheme = hasStorageTheme ? storageTheme : accountTheme;

  applyTheme(preferredTheme);
  updateActiveEntry(preferredTheme);

  if (window.matchMedia) {
    const systemTheme = window.matchMedia('(prefers-color-scheme: light)');
    const onSystemChange = () => {
      if ((root.dataset.themeMode || 'auto') === 'auto') {
        applyTheme('auto');
        updateActiveEntry('auto');
      }
    };
    if (typeof systemTheme.addEventListener === 'function') {
      systemTheme.addEventListener('change', onSystemChange);
    } else if (typeof systemTheme.addListener === 'function') {
      systemTheme.addListener(onSystemChange);
    }
  }

  const options = document.querySelectorAll('.js-theme-option');
  options.forEach((option) => {
    option.addEventListener('click', (event) => {
      event.preventDefault();
      const mode = option.dataset.theme;
      if (!mode) {
        return;
      }
      saveTheme(mode);
      updateActiveEntry(mode);
      const formId = option.dataset.themeForm;
      if (!formId) {
        return;
      }
      const form = document.getElementById(formId);
      if (form) {
        form.submit();
      }
    });
  });
})();
