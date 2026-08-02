const assert = require('node:assert/strict');
const path = require('node:path');
const test = require('node:test');

const {
  MockCustomEvent,
  MockMutationObserver,
  createDocument,
  createElement,
  installDomGlobals,
  loadScript,
  teardownDomGlobals,
} = require('./dom-harness.cjs');

function makeTimeSliderGroup({ sliderId = 'slider-1', name = 'start_delay_1', value = '20', start = '0:50', startDay = '0', min = '0', max = '90' } = {}) {
  const outer = createElement({ id: `${sliderId}-outer` });
  const middle = createElement({ id: `${sliderId}-middle` });
  const slider = createElement({ id: sliderId, tagName: 'INPUT', classNames: ['time-slider'], value, name });
  slider.attributes = {
    start: { nodeValue: start },
    startDay: { nodeValue: startDay },
  };
  slider.min = min;
  slider.max = max;

  const display = createElement({ id: `${sliderId}-display`, tagName: 'INPUT', classNames: ['time-slider-display'], value: '' });
  const dayContainer = createElement({ id: `${sliderId}-day-container`, classNames: ['time-slider-day-container'] });
  const day = createElement({ id: `${sliderId}-day`, classNames: ['time-slider-day'], innerText: '' });

  middle.appendChild(slider);
  middle.appendChild(display);
  middle.appendChild(dayContainer);
  middle.appendChild(day);
  outer.appendChild(middle);

  return { outer, middle, slider, display, dayContainer, day };
}

function setupTimeSliderEnvironment(groups) {
  const root = createElement({ tagName: 'HTML', id: 'root' });
  for (const group of groups) {
    root.appendChild(group.outer);
  }
  const document = createDocument({ root });
  installDomGlobals(document, { MutationObserver: MockMutationObserver, CustomEvent: MockCustomEvent });
  return { document, root };
}

function setupLinkSlidersEnvironment() {
  const root = createElement({ tagName: 'HTML', id: 'root' });
  const group = makeTimeSliderGroup({ sliderId: 'start-slider', name: 'start_delay_1', value: '30', start: '1:15', startDay: '2' });
  group.display.value = '1:15';
  group.day.innerText = '2';
  const duration = createElement({ id: 'duration-1', tagName: 'INPUT', name: 'duration_1' });
  duration.attributes = {
    start: { nodeValue: '' },
    startDay: { nodeValue: '' },
  };
  const eventSpy = { calls: 0, lastEvent: null };
  duration.addEventListener('startChanged', (event) => {
    eventSpy.calls += 1;
    eventSpy.lastEvent = event;
  });

  root.appendChild(group.outer);
  root.appendChild(duration);
  const document = createDocument({ root });
  installDomGlobals(document, { MutationObserver: MockMutationObserver, CustomEvent: MockCustomEvent });
  return { document, group, duration, eventSpy };
}

function setupTimeFrameVisibilityEnvironment(initialValue = '1') {
  const root = createElement({ tagName: 'HTML', id: 'root' });
  const timeFrame = createElement({ id: 'id_time_frame_field', tagName: 'SELECT', value: initialValue });
  const monthWrapper = createElement({ id: 'month-wrapper' });
  const month = createElement({ id: 'id_month_field', tagName: 'INPUT', value: '4' });
  monthWrapper.appendChild(month);
  const weekdayWrapper = createElement({ id: 'weekday-wrapper' });
  const weekday = createElement({ id: 'id_week_day_field', tagName: 'INPUT', value: '2' });
  weekdayWrapper.appendChild(weekday);
  root.appendChild(timeFrame);
  root.appendChild(monthWrapper);
  root.appendChild(weekdayWrapper);

  const calls = { save: [], restore: [] };
  const saveAndRestore = {
    save(...args) {
      calls.save.push(args);
    },
    restore(...args) {
      calls.restore.push(args);
    },
  };

  const document = createDocument({ root });
  installDomGlobals(document, { MutationObserver: MockMutationObserver, CustomEvent: MockCustomEvent, saveAndRestore });
  return { document, timeFrame, month, monthWrapper, weekday, weekdayWrapper, calls };
}

test('chickens easter egg redirects after key sequence', () => {
  const root = createElement({ tagName: 'HTML', id: 'root' });
  const document = createDocument({ root, locationHref: '/start/' });
  installDomGlobals(document, { MutationObserver: MockMutationObserver, CustomEvent: MockCustomEvent });
  loadScript(path.resolve(__dirname, '..', 'chickens.js'));

  for (const key of ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a']) {
    document.dispatchEvent({ type: 'keyup', key });
  }

  assert.equal(document.location.href, 'https://www.youtube.com/watch?v=AVlzryCQg8s');

  teardownDomGlobals();
});

test('time slider updates display and day from slider input', () => {
  const group = makeTimeSliderGroup();
  const env = setupTimeSliderEnvironment([group]);
  loadScript(path.resolve(__dirname, '..', 'time_slider.js'));
  env.document.dispatchEvent('DOMContentLoaded');

  assert.equal(group.display.value, '1:10');
  assert.equal(group.dayContainer.classList.contains('d-none'), true);
  assert.equal(group.day.innerText, '0');

  group.slider.value = '90';
  env.document.dispatchEvent({ type: 'input', target: group.slider });

  assert.equal(group.display.value, '2:20');
  assert.equal(group.dayContainer.classList.contains('d-none'), true);
  assert.equal(group.day.innerText, '0');

  group.display.value = '3:30';
  env.document.dispatchEvent({ type: 'input', target: group.display });

  assert.equal(group.slider.value, '90');
  assert.equal(group.display.value, '2:20');

  teardownDomGlobals();
});

test('time slider initializes newly observed nodes', () => {
  const group = makeTimeSliderGroup({ sliderId: 'slider-1' });
  const env = setupTimeSliderEnvironment([group]);
  loadScript(path.resolve(__dirname, '..', 'time_slider.js'));
  env.document.dispatchEvent('DOMContentLoaded');

  const newGroup = makeTimeSliderGroup({ sliderId: 'slider-2', name: 'start_delay_2', value: '15', start: '2:00', startDay: '1' });
  env.root.appendChild(newGroup.outer);
  const observer = MockMutationObserver.instances.at(-1);
  observer.trigger();

  assert.equal(newGroup.display.value, '2:15');
  assert.equal(newGroup.day.innerText, '1');

  teardownDomGlobals();
});

test('link sliders copies start values into duration target and emits startChanged', () => {
  const env = setupLinkSlidersEnvironment();
  loadScript(path.resolve(__dirname, '..', '..', '..', 'shifts', 'static', 'js', 'link_sliders.js'));
  env.document.dispatchEvent('DOMContentLoaded');

  assert.equal(env.duration.attributes.start.nodeValue, '1:15');
  assert.equal(env.duration.attributes.startDay.nodeValue, '2');
  assert.equal(env.eventSpy.calls, 1);
  assert.equal(env.eventSpy.lastEvent.target, env.duration);

  env.group.display.value = '2:05';
  env.group.day.innerText = '3';
  env.group.slider.value = '75';
  env.document.dispatchEvent({ type: 'input', target: env.group.slider });

  assert.equal(env.duration.attributes.start.nodeValue, '2:05');
  assert.equal(env.duration.attributes.startDay.nodeValue, '3');
  assert.equal(env.eventSpy.calls, 2);

  teardownDomGlobals();
});

test('time frame visibility toggles month and weekday fields', () => {
  const env = setupTimeFrameVisibilityEnvironment('1');
  loadScript(path.resolve(__dirname, '..', '..', '..', 'shifts', 'static', 'js', 'time_frame_visibility.js'));
  env.document.dispatchEvent('DOMContentLoaded');

  assert.equal(env.monthWrapper.classList.contains('d-none'), true);
  assert.equal(env.weekdayWrapper.classList.contains('d-none'), false);
  assert.equal(env.calls.save.length, 1);
  assert.equal(env.calls.restore.length, 1);

  env.timeFrame.value = '5';
  env.timeFrame.dispatchEvent({ type: 'change', target: env.timeFrame });

  assert.equal(env.monthWrapper.classList.contains('d-none'), false);
  assert.equal(env.weekdayWrapper.classList.contains('d-none'), true);
  assert.equal(env.calls.save.length, 2);
  assert.equal(env.calls.restore.length, 2);

  teardownDomGlobals();
});
