'use strict';
(function () {
  let time_frame;
  let month;
  let weekday;
  let month_label;
  let weekday_label;

  function initialize() {
    time_frame = document.getElementById('id_time_frame_field');
    month = document.getElementById('id_month_field');
    weekday = document.getElementById('id_week_day_field');
    month_label = document.getElementById('month_label');
    weekday_label = document.getElementById('week_day_label');

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
      month_label.classList.remove('d-none');
    } else {
      saveAndRestore.save(true, true, month);
      month_label.classList.add('d-none');
    }
    if (week_visible) {
      saveAndRestore.restore(true, weekday);
      weekday_label.classList.remove('d-none');
    } else {
      saveAndRestore.save(true, true, weekday);
      weekday_label.classList.add('d-none');
    }
  }

  document.addEventListener('DOMContentLoaded', initialize);
})();