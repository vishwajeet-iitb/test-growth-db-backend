from sys import stdout
from django.core.management.base import BaseCommand
from dashboard.models import Image
import os
import astropy.io.fits

class Command(BaseCommand):

    def handle(self, *args, **options):
        counts = 0
        counte = 0
        headers = {
            "date_observed":"DATE-OBS",
            "jd" :'JD',
            'proposal_no' :'PROPNUMS',
            'filter_used' : 'FILTER',
            'exposure' : 'EXPOSURE',
            'air_mass' : 'AIRMASS',
            'ccd_temp' : 'CCD_TEMP',
            'image_type' : 'IMAGETYP',
            'focus_value' : 'FOCUSER',
            'fwhm' : 'FWHM',
            'lim_mag' : 'LIM_MAG',
            'psf_mag' : 'PSF_mag', 
            'psf_merr' : 'PSF_merr', 
            'apr_mag' :0, 
            'apr_merr' :0, 
            'tel_alt' : 'TEL_ALT', 
            'tel_az' : 'TEL_AZ',  
            'ref_ra' : 'CRVAL1', 
            'ref_dec' : 'CRVAL2', 
            'tar_ra' : 'TARRA', 
            'tar_dec' : 'TARDEC', 
            'tar_name' : 'OBJECT',
        }
        PATH = '/home/adithya/iSURP/data/20211124'
        targets = [name for name in os.listdir(PATH) if os.path.exists(os.path.join(PATH,name,'reduced'))]
        print(targets)
        for folder in targets:
            url = os.path.join(PATH,folder,'reduced')
            images = [name for name in os.listdir(url) if name.endswith('.wcs.proc.fits')]
            print(images)
            for image in images:
                fits = astropy.io.fits.open(os.path.join(url,image))
                hdu = fits[0]
                try:
                    dbimage = Image(jd=hdu.header['JD'],
                                    proposal_no=hdu.header['PROPNUMS'],
                                    filepath=os.path.join(url,image),
                                    filter_used=hdu.header['FILTER'],
                                    exposure=hdu.header['EXPOSURE'],
                                    air_mass=hdu.header['AIRMASS'],
                                    ccd_temp=hdu.header['CCD_TEMP'],
                                    image_type=hdu.header['IMAGETYP'],
                                    focus_value=hdu.header['FOCUSER'],
                                    fwhm=hdu.header['FWHM'],
                                    lim_mag=hdu.header['LIM_MAG'],
                                    psf_mag=hdu.header['PSF_mag'], 
                                    psf_merr=hdu.header['PSF_merr'], 
                                    apr_mag=0, 
                                    apr_merr=0, 
                                    tel_alt=hdu.header['TEL_ALT'], 
                                    tel_az=hdu.header['TEL_AZ'],  
                                    ref_ra=hdu.header['CRVAL1'], 
                                    ref_dec=hdu.header['CRVAL2'], 
                                    tar_ra=hdu.header['TARRA'], 
                                    tar_dec=hdu.header['TARDEC'], 
                                    tar_name=hdu.header['OBJECT'],
                                    boundry_points="") #needs to set properly
                    dbimage.save()
                    counts=counts+1
                except Exception as e:
                    print("Error adding to database")
                    print(e)
                    print("file name %s"%image)
                    counte=counte+1
        
        self.stdout.write(self.style.SUCCESS("Added %s entries"%counts))
        self.stdout.write(self.style.WARNING("Unable to add %s entries"%counte))