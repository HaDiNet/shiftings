from django.forms import NumberInput


class TimeSliderWidget(NumberInput):
    template_name = 'widgets/time_slider.html'
