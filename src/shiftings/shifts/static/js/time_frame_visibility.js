'use strict';
(function () {
  let time_frame;
  let month;
  let weekday;
  let month_wrapper;
  let weekday_wrapper;

  function initialize() {
    time_frame = document.getElementById('id_time_frame_field');
    month = document.getElementById('id_month_field');
    weekday = document.getElementById('id_week_day_field');
    month_wrapper = month.parentElement;
    weekday_wrapper = weekday.parentElement;

    time_frame.addEventListener('change', onTimeFrameChange);
    onTimeFrameChange();
  }

  function onTimeFrameChange() {
    let month_visible = false;
    let week_visible = false;
    switch (time_frame.value) {
      case '1':
      case '3':
        week_visible = true;
        break;
      case '5':
      case '6':
        month_visible = true;
        break;
    }
    if (month_visible) {
      saveAndRestore.restore(true, month);
      month_wrapper.classList.remove('d-none');
    } else {
      saveAndRestore.save(true, true, month);
      month_wrapper.classList.add('d-none');
    }
    if (week_visible) {
      saveAndRestore.restore(true, weekday);
      weekday_wrapper.classList.remove('d-none');
    } else {
      saveAndRestore.save(true, true, weekday);
      weekday_wrapper.classList.add('d-none');
    }
  }

  document.addEventListener('DOMContentLoaded', initialize);
})();