(function() {
  function getElement(child, className) {
    const elements = child.parentNode.getElementsByClassName(className);
    if (elements.length !== 1) {
      throw new Error(`Didn\'t find exactly one element with the ${className} class.`);
    }
    return elements[0];
  }

  function updateSliders(slider) {
    if (!slider.name.includes('start_delay')) {
      return;
    }
    const nodes = document.getElementsByName(slider.name.replace('start_delay', 'duration'));
    if (nodes.length !== 1) {
      throw new Error('Found more or less than one end.');
    }
    const end = nodes[0];
    end.attributes.start.nodeValue = getElement(slider, 'time-slider-display').value;
    end.attributes.startDay.nodeValue = getElement(slider, 'time-slider-day').innerText;
    end.dispatchEvent(new CustomEvent('startChanged', { bubbles: true, target: end }));
  }

  document.addEventListener('input', event => {
    updateSliders(event.target);
  });

  document.addEventListener('DOMContentLoaded', () => {
    for (const slider of document.getElementsByClassName('time-slider')) {
      updateSliders(slider);
    }
  })
})();