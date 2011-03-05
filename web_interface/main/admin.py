from main.models import *
from django.contrib import admin


def mark_public(modeladmin, request, queryset):
    queryset.update(is_public=True)
mark_public.short_description = "Mark selected stories as public"

def mark_not_public(modeladmin, request, queryset):
    queryset.update(is_public=False)
mark_not_public.short_description = "Mark selected stories as not public"

class TestCaseInline(admin.TabularInline):
	model = TestCase
	extra = 5
class ProblemAdmin(admin.ModelAdmin):
    class Media:
        js = ('js/nicEdit.js','js/admin_wysiwg.js')
    list_display = ('title','is_public', 'no_of_test_cases', 'total_marks')
    list_filter = ['level', 'is_public']
    filter_horizontal = ('related_problems',)
    inlines = [TestCaseInline]
    actions = [mark_public, mark_not_public]
    search_fields = ['title', 'question']
    
class SubmissionAdmin(admin.ModelAdmin):
    class Media:
        css = {
                'all':('stylesheets/highlight.css',)
            }
    fieldsets = [
            (None,			   {'fields': ['problem', 'user', 'program', 'contest', 'language', 'marks', 'code']}),
            
    ]
    readonly_fields = ('correct', 'code', 'task_status')
    list_display = ('problem','user', 'time','program','task_status', 'marks', 'result','id','is_latest')
    list_filter = ['user', 'contest', 'time']
    search_fields = ['problem__title']
    date_hierarchy = 'time'
    def save_model(self, request, obj, form, change): 
            instance = form.save(commit=False)
            instance.save(user = request.user)
            return instance

class RankAdmin(admin.ModelAdmin):
    fieldsets = [
            (None,   {'fields': ['rank', 'user', 'contest', 'total_marks', 'not_ranked']}),
            
    ]
    readonly_fields = ('rank', 'total_marks')
    list_display = ('user', 'contest', 'rank', 'total_marks')    
    list_filter = ['contest', 'user']
    search_fields = ['user']

admin.site.register(Rank,RankAdmin)
admin.site.register(Submission,SubmissionAdmin)
admin.site.register(Problem,ProblemAdmin)
admin.site.register(Contest)
admin.site.register(Tag)
