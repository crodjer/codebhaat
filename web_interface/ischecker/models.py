import random
import sys
import urllib2
import json
import threading

from hashlib import md5
from django.db import models
from django.db.models.signals import post_save
from django.conf import settings

from main.models import Submission

IS_API_URL = "http://bazinga.interviewstreet.com/v1.0/submission"
IS_API_TOKEN = getattr(settings, "IS_API_TOKEN")

if not IS_API_TOKEN:
    raise Exception("Please provide the interviewstreet API token in your settings.py file")

class ThreadedSubmissionPost(threading.Thread):
    def __init__(self, csubmission, *args, **kwargs):
        self.csubmission = csubmission
        super(ThreadedSubmissionPost, self).__init__(*args, **kwargs)

    def run(self):
        self.csubmission.submit_to_checker()

class ThreadedSubmissionResult(threading.Thread):
    def __init__(self, csubmission, *args, **kwargs):
        self.csubmission = csubmission
        super(ThreadedSubmissionResult, self).__init__(*args, **kwargs)

    def run(self):
        self.csubmission.result_from_checker()



class CheckerSubmission(models.Model):
    key = models.CharField(max_length=32)
    submission = models.OneToOneField(Submission)
    result = models.TextField(blank=True)
    lock = models.BooleanField()

    SUCCESS = 0
    TIMELIMIT_EXCEEDED = 62
    OUTPUT_SIZE_EXCEEDED = 25
    RUNTIME_ERROR = 255

    def hash(self):
        return md5("%s-%s" %(self.submission.pk, random.getrandbits(128))).hexdigest()

    def source(self):
        return self.submission.program.read()

    def testcases(self):
        cases = []
        for case in self.submission.problem.testcase_set.all():
            cases.append(case.input_file.read())
        return cases

    def language(self):
        return self.submission.language

    def data(self):
        data = {
            'lang': self.language(),
            'source': self.source(),
            'testcases': self.testcases(),
            'hash': self.hash()
        }
        return data

    def json(self):
        return json.dumps(self.data())

    def get_result(self):
        result_json = self.checker_result()

        if not result_json:
            return False

        result = json.loads(result_json)
        result['marks'] = 0
        result['successful'] = True

        if not result['signal']:
          result['successful'] = False
          result['error'] = "Compile Error"
          return result


        for (i, case) in enumerate(self.submission.problem.testcase_set.all()):
            expected = case.output_file.read()
            output = result['stdout'][i]
            signal = result['signal'][i]
            time_taken = float(result['time'][i])
            correct = output == expected
            marks = 0


            if signal is self.SUCCESS:
                tl_soft = case.time_limit_soft
                tl_hard = case.time_limit

                if correct and time_taken <= tl_soft:
                    marks = case.marks

                elif correct and tl_soft < time_taken <= tl_hard:
                    exceed = time_taken - tl_soft
                    max_exceed = tl_hard - tl_soft
                    marks_factor = (max_exceed-exceed)/exceed
                    marks = round(case.marks*marks_factor, 2)

            elif signal is self.TIMELIMIT_EXCEEDED:
                result['successful'] = False
                result['error'] = "Runtime Exceeded"

            elif signal is self.OUTPUT_SIZE_EXCEEDED:
                result['successful'] = False
                result['error'] = "Output size exceeded"

            else:
                result['successful'] = False
                result['error'] = "Output size exceeded"

            result['marks'] += marks

            return result


    def submit_to_checker(self):
        submission_json = self.json()
        req = urllib2.Request("%s?token=%s" %(IS_API_URL, IS_API_TOKEN))
        req.add_header('Content-type', 'application/json')

        if not self.lock:
            try:
                self.lock = True
                response = urllib2.urlopen(req, submission_json).read()
                self.key = json.loads(response)['key']
                self.lock = False
                self.save()
            except urllib2.HTTPError:
                self.lock = False
                self.save()


    def result_from_checker(self):
        if not self.lock:
            try:
                self.lock = True
                self.save()
                response = urllib2.urlopen("%s?token=%s&key=%s" % (IS_API_URL,
                        IS_API_TOKEN, self.key))
                result = json.loads(response.read())['result']
                if result:
                    self.result = json.dumps(result)
                    self.lock = False
                    self.save()
            except urllib2.HTTPError:
                self.lock = False
                self.save()

        return self.result

    def checker_result(self):
        if self.key and not self.result:
            threaded_result = ThreadedSubmissionResult(self)
            if not 'test' in sys.argv:
                threaded_result.start()
            else:
                threaded_result.run()

        return self.result


    def __unicode__(self):
        return unicode(self.submission)

    @classmethod
    def submission_handler(cls, sender, instance, raw, **kwargs):
        csubmission, created = cls.objects.get_or_create(submission=instance)

        if created:
            threaded_post = ThreadedSubmissionPost(csubmission)
            if not 'test' in sys.argv:
                threaded_post.start()
            else:
                threaded_post.run()

post_save.connect(CheckerSubmission.submission_handler, Submission)
