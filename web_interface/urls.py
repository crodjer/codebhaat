from django.conf.urls.defaults import *
from django.contrib import admin
import settings
admin.autodiscover()

urlpatterns = patterns('',
    (r'', include('main.urls')),
    (r'^siteadmin/', include(admin.site.urls)),
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^ticket/', include('ticket.urls')),
    (r'^blog/', include('blog.urls')),
    (r'^accounts/', include('registration.urls')),
    url(r'^captcha/', include('captcha.urls')),
    (r'^accounts/profile/', include('profiles.urls')),
    (r'^valuate/', include('valuate.urls')),
    (r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'main/login.html'}),
    (r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'main/logout.html'}),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT, 'show_indexes': False}),                       
)
