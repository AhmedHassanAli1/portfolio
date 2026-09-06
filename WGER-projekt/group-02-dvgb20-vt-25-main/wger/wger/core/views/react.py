# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

# Django
from django.http import HttpResponseForbidden
from django.views.generic import TemplateView
from django.utils.http import urlencode
from django.shortcuts import redirect


class ReactView(TemplateView):
    """
    ReactView is a TemplateView that renders a React page.

    To get the corresponding React component, check "src/routes.tsx"
    """

    template_name = 'react/react-page.html'
    div_id = 'react-page'
    login_required = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['div_id'] = self.div_id
        context['hide_title_and_options'] = True
        return context

    def dispatch(self, request, *args, **kwargs):
        """
        Only logged-in users are allowed to access this page
        """
        if self.login_required and not request.user.is_authenticated:
            login_url = '/user/login' #string added to url to redirect to login page
            return redirect(f'{login_url}?next={request.get_full_path()}') #redirect to new url (/user/login +?next 
            # + url of page user is trying to vist), takes you to place you were supposed to go to after logging in

        return super().dispatch(request, *args, **kwargs)
