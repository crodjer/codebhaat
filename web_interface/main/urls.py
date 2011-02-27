from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    (r'^$', 'main.views.home'),
    (r'^contest/$', 'main.views.contest_page'),
    url(r'^contest/problems-by-tag/(?P<tag>.*)/$', 'main.views.contest_page', name='problems_display_tag'),
    url(r'^contest/problems-by-category/(?P<category>.*)/$', 'main.views.contest_page', name='problems_display_category'),
    (r'^contest/problem/(?P<problem_id>\d+)/$', 'main.views.problem_detail'),
    (r'^contest/problem/(?P<problem_id>\d+)/input/(?P<testcase_id>\d+)/testinput.in$', 'main.views.problem_input'),
    (r'^contest/problem/(?P<problem_id>\d+)/output/(?P<testcase_id>\d+)/testoutput.out$', 'main.views.problem_output'),
    (r'^register/a/team/(?P<team_id>\d+)/(?P<team_name>\w+)/(?P<password>\w+)/(?P<email>[-_.@\w]+)/$', 'main.views.reg_team'),
    (r'^credits/$', 'main.views.credits'),                       
    (r'^error/$', direct_to_template , {'template':'main/error.html'}),
)
