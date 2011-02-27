from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    (r'^$', 'main.views.home'),
    (r'^contest/$', 'main.views.categories'),    
    url(r'^contest/(?P<category_pk>\d+)/$', 'main.views.problem_list', name='category_problems'),
    url(r'^problem/(?P<problem_pk>\d+)/$', 'main.views.problem_detail', name='problem_detail'),
    url(r'^problem/(?P<problem_pk>\d+)/input/(?P<testcase_id>\d+)/testinput.in$', 'main.views.problem_input'),
    url(r'^problem/(?P<problem_pk>\d+)/output/(?P<testcase_id>\d+)/testoutput.out$', 'main.views.problem_output'),
    url(r'^register/a/team/(?P<team_id>\d+)/(?P<team_name>\w+)/(?P<password>\w+)/(?P<email>[-_.@\w]+)/$', 'main.views.reg_team'),
    url(r'^credits/$', 'main.views.credits'),                       
    url(r'^error/$', direct_to_template , {'template':'main/error.html'}),
)
