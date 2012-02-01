from django.contrib import admin
from blog.models import Entry

class EntryAdmin(admin.ModelAdmin):
    class Media:
        js = ('js/nicEdit.js','js/admin_wysiwg.js')
        list_display = ('pub_date', 'headline', 'author')

admin.site.register(Entry, EntryAdmin)
