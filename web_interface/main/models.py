from django.template.defaultfilters import filesizeformat
from django.core.urlresolvers import reverse
from django.db import models
from django import forms
from picklefield import PickledObjectField
from django.contrib.auth.models import User
from django.forms import HiddenInput
from main.tasks import submit, SubmitTask
from django.core.files.storage import FileSystemStorage
import settings, os, datetime, re
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from django.db.models import Sum
from django.forms.fields import DateField, ChoiceField, MultipleChoiceField
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from django.forms.extras.widgets import SelectDateWidget

STORAGE_PATH = os.path.join(settings.ROOT_PATH, 'files')
fs = FileSystemStorage(location=STORAGE_PATH)

TAG_RE = re.compile('[^a-z0-9\-_\+\:\.]?', re.I)

class RankManager(models.Manager):
    def get_or_set(self, user, contest, *args, **kwargs):
        rank, new = self.get_or_create(user=user, contest=contest, *args, **kwargs)
        if new:
            if rank.user.has_perm('cannot_be_ranked'):
                rank.not_ranked = True
            rank.update()
        return rank

    def update_all(self, contests):
        for contest in contests:
            for user in User.objects.all():
              Rank.objects.get_or_set(user, contest)
        return True

class Contest(models.Model):
    name = models.CharField('Name', max_length = 100, unique=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('contest_problems', kwargs={'contest_pk': self.pk})

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.name

    @staticmethod
    def clean_tag(name):
        """Replace spaces with dashes, in case someone adds such a tag manually"""

        name = name.replace(' ', '-')
        name = TAG_RE.sub('', name)
        return name.lower().strip()

    def save(self, *args, **kwargs):
        """Cleans up any characters I don't want in a URL"""

        self.name = Tag.clean_tag(self.name)
        super(Tag, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('problems_display_tag', (self.name,))

    class Meta:
        ordering = ('name',)

class Rank(models.Model):
    user            =  models.ForeignKey(User)
    contest         = models.ForeignKey(Contest)
    total_marks     = models.FloatField(default=0.0)
    not_ranked      = models.BooleanField(default=False)

    objects = RankManager()
    def get_total_marks(self):
        submissions = self.user.submission_set.filter(is_latest=True,
                                                      contest=self.contest).aggregate(Sum('marks'))
        total_marks = submissions['marks__sum']
        if not total_marks:
            return 0.0
        return total_marks

    def __unicode__(self):
        return '%s\'s rank in %s' %(self.user, self.contest)

    def rank(self):
        contest_ranks = self.contest.rank_set.all()
        if self.total_marks and not self.not_ranked:
            rank = contest_ranks.filter(total_marks__gt=self.total_marks,
                                        not_ranked=False).count()+1
            return rank
        else:
            return 'N/A'

    def update(self, *args, **kwargs):
        self.total_marks=self.get_total_marks()
        self.save()

    class Meta:
        ordering = ['-total_marks']
        permissions = (
                    ('cannot_be_ranked', 'User cannot be ranked amongst public'),
                )

#The programming problem
class Problem(models.Model):
    LEVEL_CHOICES = (
            (1, 'Easy'),
            (2, 'Medium'),
            (3, 'Hard'),
        )
    title = models.CharField('Title', max_length = 100)
    question = models.TextField('Question')
    is_public = models.BooleanField('Is Public')
    contest = models.ForeignKey(Contest, verbose_name='contest', blank=False)
    tags = models.ManyToManyField(Tag, help_text= 'Tags that describe this problem', blank=True)
    related_problems = models.ManyToManyField('self', blank=True)
    publish_date = models.DateTimeField(default=datetime.datetime.now, help_text='The date and time this problem shall appear online.')
    level = models.IntegerField('level', choices=LEVEL_CHOICES, default=2)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self, contest):
        if not contest:
          return reverse('problem_detail', kwargs={'problem_pk': self.pk, 'contest_pk':self.contest.pk})
        else:
          return reverse('problem_detail', kwargs={'problem_pk': self.pk, 'contest_pk':contest.pk})

    def no_of_test_cases(self):
        return self.testcase_set.count()

    def status_image(self, user):
        try:
            latest_submission = self.submission_set.get(user=user, is_latest=True)
            return latest_submission.status_image()
        except:
            return ('icon_alert.gif', 'Not attempted')


    def status(self):
        submissions = self.submission_set.filter(is_latest=True)
        latest_submissions = submissions.filter(is_latest=True).order_by('-time')
        successful_submissions = 0
        success_rate = 0
        total_submissions = submissions.count()
        for submission in submissions:
            if submission.ready() and submission.correct():
                successful_submissions+=1

        if total_submissions:
            success_rate = int(100.0*successful_submissions/total_submissions)
        return {'total_submissions':total_submissions, 'successful_submissions':successful_submissions, 'success_rate': success_rate, 'latest_submissions': latest_submissions[:10]}
    def total_marks(self):
        marks = 0
        for case in self.testcase_set.all():
            marks += case.marks
        return marks

# A problem that is contributed by a user
class ContribProblem(models.Model):
      user = models.ForeignKey(User)
      LEVEL_CHOICES = (
              (1, 'Easy'),
              (2, 'Medium'),
              (3, 'Hard'),
          )
      title = models.CharField('Title', max_length = 200)
      question = models.TextField('Question')
      tags = models.ManyToManyField(Tag, help_text= 'Tags that describe this problem', blank=True)
      level = models.IntegerField('level', choices=LEVEL_CHOICES, default=2)

      def save(self, user=None, *args, **kwargs):
        if user:
          self.user = user
        super(ContribProblem, self).save(*args, **kwargs)


class ContribForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ContribForm, self).__init__(*args, **kwargs)
        # Set widget size options
        self.fields['title'].widget.attrs["size"] = 40
        self.fields['question'].widget.attrs["cols"] = 50

    class Meta:
        model = ContribProblem
        fields = ['title','level','question','tags']
        #filename = forms.CharField(widget=HiddenInput())


# A tutorial model for problems
class Tutorial(models.Model):
  tutorial = models.TextField('Content')
  problem = models.ForeignKey(Problem, unique=True)
  # A tutorial might not be still available for display
  is_visible = models.BooleanField('Is visible', default = False)

#Input Output file for problem
class TestCase(models.Model):
    problem = models.ForeignKey(Problem)
    input_file = models.FileField('Input File', upload_to = 'inputs', storage=fs)
    output_file = models.FileField('Output File', upload_to = 'outputs', storage=fs)
    time_limit_soft = models.FloatField('Soft Time Limit (Seconds)', default = 0.5)
    time_limit = models.FloatField('Time Limit (Seconds)', default = 2)
    is_public = models.BooleanField('Is Public', default = False)
    marks = models.IntegerField('Marks', default = 10)
    def __unicode__(self):
        return self.problem.title + ': Input/Output'
    def input_url(self):
        return '/problem/%d/input/%d/testinput.in' %(self.problem.id, self.id)
    def output_url(self):
        return '/problem/%d/output/%d/testoutput.out' %(self.problem.id, self.id)
    def weightage(self):
        weight = (float(self.marks)/float(self.problem.total_marks()))*100
        return str("%.2f"%(weight)+ " %")

#The submissions from a user are defined here
class Submission(models.Model):

    CODE_LANGUAGES = (
        (1, 'C'),
        (2, 'C++'),
        (3, 'Sun Java'),
        (4, 'Open Java'),
        (5, 'Python'),
        (6, 'Perl'),
        (7, 'PHP'),
        (8, 'Ruby'),
        (9, 'C#'),
        (12, 'Haskell'),
        (13, 'Clojure'),
        (14, 'Bash'),
        (15, 'Scala'),
        (16, 'Erlang')
    )

    LANGUAGES = tuple((str(code), name) for (code, name) in CODE_LANGUAGES)

    user = models.ForeignKey(User)
    language = models.CharField('Language', max_length = 10, choices=LANGUAGES)
    program = models.FileField('Code', upload_to = 'programs', storage=fs)
    problem = models.ForeignKey(Problem)
    contest = models.ForeignKey(Contest)
    filename = models.CharField('Filename', max_length = 50)
    time = models.DateTimeField('Time', auto_now_add=True)
    is_latest = models.BooleanField('Latest', default = True)
    celery_task = PickledObjectField()  #This saves the result of the celery_task, It gives the key to access the celery task database.
    marks = models.IntegerField('Marks', blank=True, null=True)
    class Meta:
        ordering = ['-time']
        get_latest_by = 'time'

    def __unicode__(self):
        return self.problem.title + ' by ' + str(self.user) + ', File: ' + str(self.program)

    #Get the current status of the process
    def attempts(self):
        total_attempts = Submission.objects.filter(user = self.user, problem = self.problem).count()
        return total_attempts

    def correct(self):
        try:
            return self.result().get('successful', False)
        except AttributeError:
            return False

    def delete(self,*args, **kwargs ):
        old_submissions = Submission.objects.exclude(pk=self.id).filter(user = self.user, problem = self.problem)
        self.set_latest(old_submissions)
        super(Submission, self).delete(*args, **kwargs)

    def day_diff(self):
        days = (datetime.datetime.now()-self.time).days
        return days

    def result(self):
        return self.checkersubmission.get_result()

    def ready(self):
        ready = True if self.checkersubmission.result else False
        if ready and self.is_latest and not self.marks:
            self.set_marks()
            self.set_rank()

        return ready

    def status(self):
        if self.ready():
            return 'Correct' if self.correct() else 'Wrong'
        else:
            return 'Processing'

    def code(self):
        pygmented_code = highlight(self.program.read(), PythonLexer(), HtmlFormatter())
        return pygmented_code
    code.allow_tags = True

    def save(self,user=None,problem=None,contest=None, *args, **kwargs):
        if not self.pk: 
            if user:
                self.user = user
            if problem:
                self.problem = problem
            if contest:
                self.contest=contest
            self.filename = str(self.program)
            #self.celery_task = SubmitTask.apply_async(args = self.task_detail())
            self.update_old_submissions()

        super(Submission, self).save(*args, **kwargs)

    def set_latest(self, submissions):
        print 'setting latest'
        latest_submission = submissions.latest()
        latest_submission.is_latest = True
        latest_submission.save()
        return latest_submission

    def status_image(self):
        if not self.ready():
            return ('icon_clock.gif', 'Submission under evaluation')
        elif self.correct():
            return ('icon_success.gif', 'Correct submission')
        else:
            return ('icon_error.gif', 'Wrong attempt')

    def update_old_submissions(self):
        old_submissions = Submission.objects.filter(is_latest=True, user=self.user, problem=self.problem)
        old_submissions.update(is_latest=False)

    def task_status(self):
        if self.ready():
            return 'Processed'
        else:
            return 'In Queue'

    def set_marks(self):
        self.marks = self.result()['marks']
        self.save()

    def set_rank(self):
        rank = Rank.objects.get_or_set(self.user, self.contest)
        rank.update()
        return rank

    def task_detail(self):
        tests = []
        time_limit = None
        for case in self.problem.testcase_set.all():
            time_limit = max(time_limit, case.time_limit) if time_limit else case.time_limit
            tests.append({'input':case.input_file.read(), 'output':case.output_file.read(), 'time_limit_soft':case.time_limit_soft, 'time_limit':case.time_limit, 'marks': case.marks})
        return [self.problem, self.language, self.program.read(),self.filename,tests, time_limit]

#Form for a submission to be made by the user
class SubmissionForm(forms.ModelForm):
    def clean_program(self):
        program = self.cleaned_data['program']
        if program._size > settings.MAX_UPLOAD_SIZE:
            error = 'Please keep filesize under %s, yours was %s.' %(filesizeformat(settings.MAX_UPLOAD_SIZE),
                                                                     filesizeformat(program._size)
                                                                     )
            raise forms.ValidationError(error)
        return program

    class Meta:
        model = Submission
        fields = ['language','program']
        filename = forms.CharField(widget=HiddenInput())
