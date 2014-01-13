from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'eyeapp.views.home'),
    url(r'^upload$', 'eyeapp.views.upload'),
    url(r'^you$', 'eyeapp.views.you'),
    url(r'^explore$', 'eyeapp.views.explore'),
    url(r'^user$', 'eyeapp.views.user'),
    url(r'^post$', 'eyeapp.views.post'),
    url(r'^pinfo$','eyeapp.views.pinfo'),
    url(r'^comment$','eyeapp.views.comment'),
    url(r'^gallery$','eyeapp.views.gallery'),
    # build-in login and logout
    url(r'^login$', 'django.contrib.auth.views.login',{'template_name':'eyeapp/login.html'},name='login'),
   # url(r'^login$','eyeapp.views.sign_in',name='login'),
    url(r'^logout$','django.contrib.auth.views.logout_then_login',name='logout'),
    url(r'^register$','eyeapp.views.register',name='register'),
    url(r'^confirm-registration/(?P<username>[a-zA-Z0-9_@\+\-]+)/(?P<token>[a-z0-9\-]+)$', 'eyeapp.views.confirm_registration', name='confirm'),
)
