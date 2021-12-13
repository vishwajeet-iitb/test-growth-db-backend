from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Proposal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    heading = models.CharField(max_length=255)

class Image(models.Model):
    date_observed = models.DateField(auto_now=False,auto_now_add=True) #has to be changed
    jd = models.FloatField(unique=True,blank=False)
    proposal_no = models.CharField(max_length=20)

    filter_used = models.CharField(max_length=20)
    exposure = models.FloatField()
    air_mass = models.FloatField()
    ccd_temp = models.FloatField()
    image_type = models.CharField(max_length=20) 
    focus_value = models.CharField(max_length=20)
    fwhm = models.FloatField()
    lim_mag = models.FloatField()
    psf_mag = models.FloatField()
    psf_merr = models.FloatField()
    apr_mag = models.FloatField() #check this header key for this
    apr_merr = models.FloatField() #check this header key for this

    filepath = models.CharField(max_length=120, unique=True, blank=False)

    tel_alt = models.FloatField()
    tel_az = models.FloatField()

    ref_ra =  models.FloatField()
    ref_dec = models.FloatField()

    tar_ra = models.FloatField()
    tar_dec = models.FloatField()
    tar_name = models.CharField(max_length=20)

    boundry_points = models.CharField(max_length=120)

    # def __repr__(self):
    #     attrs = vars(self)
    #     for index,vals in attrs.items():
    #         if not index.startswith('__') and attrs[index]==None:
    #             attrs[index] = float("Nan")
    #     return ', '.join("{}".format(item) for item in attrs.items())