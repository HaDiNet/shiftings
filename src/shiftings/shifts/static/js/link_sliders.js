(function() {
  function getElement(child, className) {
    const elements = child.parentNode.getElementsByClassName(className);
    if (elements.length !== 1) {
      throw new Error(`Didn\'t find exactly one element with the ${className} class.`);
    }
    return elements[0];
  }

  document.addEventListener('input', event => {
    const element = event.target;
    if (element.name.includes('start_delay')) {
      const nodes = document.getElementsByName(element.name.replace('start_delay', 'duration'));
      if (nodes.length !== 1) {
        throw new Error('Found more or less than one end.');
      }
      const end = nodes[0];
      end.attributes.start.nodeValue = getElement(element, 'time-slider-display').value;
      end.attributes.startDay.nodeValue = getElement(element, 'time-slider-day').innerText;
      end.dispatchEvent(new CustomEvent('startChanged', {bubbles: true, target: end}));
    }
  });
})();