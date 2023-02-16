from typing import Any, Optional

from django.urls import reverse
from django.views.generic import RedirectView


class LandingPageView(RedirectView):
    def get_redirect_url(self, *args: Any, **kwargs: Any) -> Optional[str]:
        if self.request.user.is_authenticated:
            return reverse('overview_thismonth')
        return reverse('login')
