from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Proposal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    heading = models.CharField(max_length=255)

class Image(models.Model):
    jd = models.FloatField(blank=False)
    date_observed = models.DateTimeField(auto_now=False,auto_now_add=False) 
    exposure = models.FloatField(null=True, blank=True)
    tar_ra = models.FloatField(null=True, blank=True)
    tar_dec = models.FloatField(null=True, blank=True)
    tar_name = models.CharField(max_length=20, blank=True)


    ccd_temp = models.FloatField(null=True, blank=True)
    tel_alt = models.FloatField(null=True, blank=True)
    tel_az = models.FloatField(null=True, blank=True)
    air_mass = models.FloatField(null=True, blank=True)
    hour_angle = models.FloatField(null=True, blank=True)
    avg = models.FloatField(null=True, blank=True)
    stdev = models.FloatField(null=True, blank=True)
    filter_used = models.CharField(max_length=20,null=True, blank=True)
    diff_exists = models.CharField(max_length=3,null=True, blank=True) 
    focus_value = models.CharField(max_length=20,null=True, blank=True)
    ra_rate = models.FloatField(null=True, blank=True)
    dec_rate = models.FloatField(null=True, blank=True)
    proposal_no = models.CharField(max_length=20,null=True, blank=True)
    progid = models.CharField(max_length=20,null=True, blank=True)
    pi = models.CharField(max_length=20,null=True, blank=True)
    tile_id = models.FloatField(null=True, blank=True)
    
    
    fwhm = models.FloatField(null=True, blank=True)
    lim_mag = models.FloatField(null=True, blank=True)
    lim_mag3 = models.FloatField(null=True, blank=True)
    psf_mag = models.FloatField(null=True, blank=True)
    psf_merr = models.FloatField(null=True, blank=True)
    psf_type = models.CharField(max_length=20,null=True, blank=True)
    psf_zerr = models.FloatField(null=True, blank=True)
    psf_zp = models.FloatField(null=True, blank=True)

    filepath = models.CharField(max_length=120, unique=True, blank=False)

    ref_ra =  models.FloatField(null=True, blank=True)
    ref_dec = models.FloatField(null=True, blank=True)

    healpy_pxl = models.IntegerField(null=True, blank=True)

    headers = {
            "jd" :'JD',
            "date_observed":"DATE-OBS",
            'exposure' : 'EXPTIME',
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