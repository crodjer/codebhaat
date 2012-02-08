import akismet
import datetime
from django.conf import settings
from django.db import models
from django.contrib.sites.models import Site
from django.contrib.comments.signals import comment_was_posted
from django.utils.encoding import smart_str
from django.contrib.auth.models import User

class Entry(models.Model):
    pub_date = models.DateTimeField()
    slug = models.SlugField(unique_for_date='pub_date')
    headline = models.CharField(max_length=200)
    summary = models.TextField(help_text="Use raw HTML.")
    body = models.TextField(help_text="Use raw HTML.")
    user = models.ForeignKey(User)

    class Meta:
        db_table = 'blog_entries'
        verbose_name_plural = 'entries'
        ordering = ('-pub_date',)
        get_latest_by = 'pub_date'

    def __unicode__(self):
        return self.headline

    def get_absolute_url(self):
        return "/weblog/%s/%s/" % (self.pub_date.strftime("%Y/%b/%d").lower(), self.slug)

    @property
    def comments_enabled(self):
        delta = datetime.datetime.now() - self.pub_date
        return delta.days < 60

def moderate_comment(sender, comment, request, **kwargs):
    return
    ak = akismet.Akismet(
        key = settings.AKISMET_API_KEY,
        blog_url = 'http://%s/' % Site.objects.get_current().domain
    )
    data = {
        'user_ip': request.META.get('REMOTE_ADDR', '127.0.0.1'),
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'referrer': request.META.get('HTTP_REFERRER', ''),
        'comment_type': 'comment',
        'comment_author': smart_str(comment.user_name),
    }
    if ak.comment_check(smart_str(comment.comment), data=data, build_data=True):
        comment.is_public = False
        comment.save()

comment_was_posted.connect(moderate_comment)
