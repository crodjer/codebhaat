from django.db import models
from django.db.models.fields import *
from django.contrib.auth.models import User

class ProfileManager(models.Manager):
    """ Custom manager for the "UserProfile" model. """
    def profile_callback(self, user):
        """ Creates user profile while registering new user registration/urls.py """
        new_profile = UserProfile.objects.create(user=user,)

class UserProfile(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    HALL_CHOICES = (
                        ('1', 'AZAD'),
                        ('2', 'BCROY'),
                        ('3', 'GHOKLE'),
                        ('4', 'HJB'),
                        ('5', 'JCB'),
                        ('6', 'LLR'),
                        ('7', 'MMM'),
                        ('8', 'NEHRU'),
                        ('9', 'PATEL'),
                        ('10', 'RK'),
                        ('11', 'RP'),
                        ('12', 'SN/MT/IG'),
                        ('13', 'VS'),
                        ('14', 'ZH'),
                        ('15', 'MS'),
                        ('16', 'SAM'),
                       )
    YEAR_CHOICES = (
                 ('1', '1st Year'),
                 ('2', '2nd Year'),
                 ('3', '3rd Year'),
                 ('4', '4th Year'),
                 ('5', '5th Year'),
                 ('6', 'Postgraduate'),
                 ('9', 'Other'),
                 )
    name = models.CharField("Full Name", max_length=100, unique=True)
    gender = models.CharField("Gender", max_length=1, choices=GENDER_CHOICES)
    hall = models.CharField("Hall", max_length=4, choices=HALL_CHOICES)
    room = models.CharField("Room No.", max_length=10,)
    year = models.CharField("Year", max_length=1, choices=YEAR_CHOICES)
    roll_no = models.CharField("Roll No.", max_length=10) 
    user = models.ForeignKey(User, unique=True)
    objects = ProfileManager()

    def __unicode__(self):
        return self.name.title()
    
    def get_absolute_url(self):
        return ('profiles_profile_detail', (), { 'username': self.user.username }) 
