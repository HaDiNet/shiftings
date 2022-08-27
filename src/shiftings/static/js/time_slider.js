(function () {
  const initialized = [];

  function getElement(child, className) {
    const elements = child.parentNode.getElementsByClassName(className);
    if (elements.length !== 1) {
      throw new Error(`Didn\'t find exactly one element with the ${className} class.`);
    }
    return elements[0];
  }

  function sliderChanged(slider) {
    let minutes = parseInt(slider.value);
    let hours = Math.floor(minutes / 60);
    minutes = minutes - (hours * 60);

    const start = slider.attributes.start.nodeValue;
    const index = start.indexOf(':');
    hours += parseInt(start.substring(0, index));
    minutes += parseInt(start.substring(index + 1));
    if (minutes >= 60) {
      minutes -= 60;
      hours++;
    }

    const days = parseInt(slider.attributes.startDay.nodeValue) + Math.floor(hours / 24);
    hours %= 24;
    if (minutes < 10) {
      minutes = '0' + minutes;
    }
    getElement(slider, 'time-slider-display').value = `${hours}:${minutes}`;
    getElement(slider, 'time-slider-day-container').classList.toggle('d-none', days === 0);
    getElement(slider, 'time-slider-day').innerText = `${days}`;
  }

  function displayChanged(display) {
    if (display.reportValidity()) {
      const hours = parseInt(display.value.substring(0, display.value.indexOf(':')));
      const minutes = parseInt(display.value.substring(display.value.indexOf(':') + 1));
      const slider = getElement(display, 'time-slider');
      let total = hours * 60 + minutes;
      if (total > slider.max) {
        total = slider.max;
      } else if (total < slider.min) {
        total = slider.min;
      }
      slider.value = total;
      sliderChanged(slider);
    }
  }

  document.addEventListener('input', event => {
    const element = event.target;
    if (element.classList.contains('time-slider')) {
      sliderChanged(element);
    } else if (element.classList.contains('time-slider-display')) {
      displayChanged(element);
    }
  });
  document.addEventListener('startChanged', event => {
    const element = event.target;
    if (element.classList.contains('time-slider')) {
      sliderChanged(element);
    }
  });

  function initSliders() {
    for (const slider of document.getElementsByClassName('time-slider')) {
      if (!initialized.includes(slider)) {
        initialized.push(slider);
        sliderChanged(slider);
      }
    }
  }

  function initialize() {
    initSliders();
    new MutationObserver(() => initSliders()).observe(document.documentElement, { childList: true, subtree: true });
  }

  document.addEventListener('DOMContentLoaded', () => initialize());
})();