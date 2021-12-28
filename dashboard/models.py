from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Proposal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    heading = models.CharField(max_length=255)

class Image(models.Model):
    jd = models.FloatField(unique=True,blank=False)
    date_observed = models.DateTimeField(auto_now=False,auto_now_add=False) 
    exposure = models.FloatField()
    tar_ra = models.FloatField()
    tar_dec = models.FloatField()
    tar_name = models.CharField(max_length=20)


    ccd_temp = models.FloatField()
    tel_alt = models.FloatField()
    tel_az = models.FloatField()
    air_mass = models.FloatField()
    hour_angle = models.FloatField()
    avg = models.FloatField()
    stdev = models.FloatField()
    filter_used = models.CharField(max_length=20)
    image_type = models.CharField(max_length=20) 
    focus_value = models.CharField(max_length=20)
    ra_rate = models.FloatField()
    dec_rate = models.FloatField()
    proposal_no = models.CharField(max_length=20)
    progid = models.CharField(max_length=20)
    pi = models.CharField(max_length=20)
    tile_id = models.FloatField()
    
    
    fwhm = models.FloatField()
    lim_mag = models.FloatField()
    lim_mag3 = models.FloatField()
    psf_mag = models.FloatField()
    psf_merr = models.FloatField()
    psf_type = models.CharField(max_length=20)
    psf_zerr = models.FloatField()
    psf_zp = models.FloatField()

    filepath = models.CharField(max_length=120, unique=True, blank=False)

    ref_ra =  models.FloatField()
    ref_dec = models.FloatField()

    boundry_points = models.CharField(max_length=120,blank=True)

    headers = {
            "jd" :'JD',
            "date_observed":"DATE-OBS",
            'exposure' : 'EXPOSURE',
            'tar_name' : 'OBJECT',
            'ccd_temp' : 'CCD_TEMP',
            'tel_alt' : 'TEL_ALT', 
            'tel_az' : 'TEL_AZ',  
            'air_mass' : 'AIRMASS',
            'hour_angle':'HA',
            'avg': 'AVERAGE',
            'stdev': 'STDEV',
            'filter_used' : 'FILTER',
            'focus_value' : 'FOCUSER',
            'image_type' : 'IMAGETYP',
            'ra_rate':'RA-RATE',
            'dec_rate':'DEC-RATE',
            'proposal_no' :'PROPNUMS',
            'progid':'PROGID',
            'pi':'PI',
            'tile_id':'TILE_ID',
            'fwhm' : 'FWHM',
            'lim_mag' : 'LIM_MAG',
            'lim_mag3' : 'LIM_MAG3',
            'psf_mag' : 'PSF_mag', 
            'psf_merr' : 'PSF_merr', 
            'psf_type':'PSF_TYPE',
            'psf_zp':'PSF_ZP',
            'psf_zerr':'PSF_ZERR',
            'ref_ra' : 'CRVAL1', 
            'ref_dec' : 'CRVAL2', 
            'tar_ra' : 'TARRA', 
            'tar_dec' : 'TARDEC', 
        }
    

    # def __repr__(self):
    #     attrs = vars(self)
    #     for index,vals in attrs.items():
    #         if not index.startswith('__') and attrs[index]==None:
    #             attrs[index] = float("Nan")
    #     return ', '.join("{}".format(item) for item in attrs.items())