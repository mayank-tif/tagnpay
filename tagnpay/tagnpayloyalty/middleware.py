from django.shortcuts import redirect, render
from django.contrib.auth import logout
from django.urls import resolve
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.contrib.sessions.middleware import SessionMiddleware
from django.utils.deprecation import MiddlewareMixin

class SessionCheckByMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Define the views that should be exempt from session checking

        self.exempt_apps = ['RFAPIS','MAppApis']

        self.exempt_views = [
            'tagnpayloyalty.views.View_platformlogin',  # Example: Exempt login view
            #'tagnpayloyalty.views.View_UserRegistration',  # Example: Exempt signup view
            'login',
            # Add more exempt views here
        ]

        self.exempt_urls = [
            'tagnpayloyaltyadmin:index',
            'tagnpayloyaltyadmin:login',
            'tagnpayloyaltyadmin:password_change',
            'tagnpayloyaltyadmin:logout',
            # Add more if needed
        ]

    def __call__(self, request):
        # Get the name of the currently requested view
        current_app_name = resolve(request.path_info).app_name
        current_view = resolve(request.path_info).view_name
        current_url_name = resolve(request.path_info).url_name
        

        #print(current_view)
        #print(timezone.now())
        #print(current_app_name)

        if current_app_name in self.exempt_apps:
            return self.get_response(request)
        
        # Check if the current view is in the exempt_views list
        if current_view in self.exempt_views:
            # Skip session check for exempt views
            return self.get_response(request)
        
        if current_url_name in self.exempt_urls:
            return self.get_response(request)
        
        if request.path.startswith('/tagnpayloyaltyadmin/'):
            return self.get_response(request)

        # If the session is not active, redirect to the login page
        if not self.is_session_active(request):
            #return redirect(settings.LOGIN_URL)
            logout(request)
            #return redirect('')
            return HttpResponseRedirect(reverse('login') + '?msg=expired')
            #return render(request,'index.html',{"message":"Session expired!!"})  # Redirect to login or your preferred page


        # If the session is active, continue processing the request
        response = self.get_response(request)
        return response

    def is_session_active(self, request):
        # Check if the user is authenticated and session contains a specific key
        #if request.user.is_authenticated and 'loginid' in request.session:
        if request.session.get('is_active') and 'loginid' in request.session:
            return True
        return False
    

class CustomSessionMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.session_middleware = SessionMiddleware(get_response)

    def __call__(self, request):
        # Check if the request path matches the custom admin URL path
        if not request.path.startswith('/tagnpayloyaltyadmin/'):  # Adjust to your actual admin URL path
            # If not admin path, process session as usual
            self.session_middleware.process_request(request)

        # Proceed with the rest of the middleware chain
        response = self.get_response(request)

        # Apply the session middleware response process for non-admin paths
        if not request.path.startswith('/tagnpayloyaltyadmin/'):
            self.session_middleware.process_response(request, response)

        return response