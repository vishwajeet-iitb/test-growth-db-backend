from genericpath import isdir
from math import nan
from django.core.management.base import BaseCommand
import pytz
from GrowthInterface import settings
from dashboard.models import Image
import datetime
from django.utils import dateparse
import os, warnings
import astropy.io.fits
import numpy as np
import healpy as hp
import astropy.wcs as wcs

class Command(BaseCommand):

    def add_arguments(self, parser) :
        parser.add_argument('--add',help="Add a single image from a path")
        parser.add_argument('--dir',help="Add images from a path")
        parser.add_argument('--date',help="Add all images from a day")
        parser.add_argument('-i', nargs=3, help="Find folders of days and add them. Provide path, startdate, enddate in the format yyyymmdd")
        parser.add_argument('--migrate', nargs=2 ,help='Migrate file path to NAS. Inputs - date in format yyyymmdd and new path including the folder name')
        parser.add_argument('--remake', help='Add new fields to database based on headers of fits file')
        parser.add_argument('--use_header_file',help="False if respective header file should not be used for making the database")
        parser.add_argument('-u',help="Update healpxls")

    def handle(self, *args, **options):
        count_s = 0
        count_err = 0
        countedit = 0
        
        add = options['add']
        folder = options['dir']
        day = options['date']
        bulk = options['i']
        migrateData = options['migrate']
        remakeParam = options['remake']
        headerRequired = False if options['use_header_file']=='False' else True        
        healpxlUpdate = options['u']

        if healpxlUpdate:
            self.update_healpxl()
            return

        if add != None and folder == None and day == None and bulk == None and migrateData == None and remakeParam == None:
            if not os.path.exists(add):
                self.stdout.write(self.style.ERROR("Path does not exist"))
                return
            
            try:
                res = self.addImage(add, headerRequired)
            except:
                res = 0
                print('Unable to add filename ', add)
            
            if res == 0:
                count_err = count_err+1
            elif res == 2:
                count_s = count_s+1
            elif res == 1:
                countedit = countedit+1
        
        elif add == None and folder != None and day == None and bulk == None and migrateData == None and remakeParam == None:
            
            if not os.path.exists(folder):
                self.stdout.write(self.style.ERROR("Path does not exist"))
                return
            
            [count_s,count_err,countedit] = self.addImages(folder, headerRequired)   
        
        elif add == None and folder == None and day != None and bulk == None and migrateData == None and remakeParam == None:
            
            if not os.path.exists(day):
                self.stdout.write(self.style.ERROR("Path does not exist"))
                return
            
            [count_s,count_err, countedit] = self.addDay(day, headerRequired)
        
        elif add == None and folder == None and day == None and bulk != None and migrateData == None and remakeParam == None:
            # import all data
            day1 = bulk[1]
            day2 = bulk[2]
            PATH = bulk[0]
            
            if not os.path.exists(PATH):
                self.stdout.write(self.style.ERROR("Path does not exist"))
                return
            
            try:
                start = datetime.datetime.strptime(day1,'%Y%m%d')
                end = datetime.datetime.strptime(day2,'%Y%m%d')
            except:
                self.stdout.write(self.style.ERROR("Check the dates again"))
            else:
                while start <= end:
                    name = start.strftime('%Y%m%d')
                    print(name)
                    if os.path.exists(os.path.join(PATH,name)):
                        [success,fail,edit] = self.addDay(os.path.join(PATH,name), headerRequired)
                        count_s = count_s + success
                        count_err = count_err + fail
                        countedit = countedit + edit
                    else:
                        self.stdout.write(self.style.WARNING("Folder of %s does not exists"%name))

                    start = start + datetime.timedelta(days=1)
                
        elif add == None and folder == None and day == None and bulk == None and migrateData != None and remakeParam == None:
            self.migrateDataNAS(migrateData[0],migrateData[1])
        
        elif add == None and folder == None and day == None and bulk == None and migrateData == None and remakeParam != None:
            self.remakeDB(remakeParam)
        
        else:
            self.stdout.write(self.style.ERROR("Unknown command"))

        if migrateData == None and remakeParam == None:
            self.stdout.write(self.style.SUCCESS("Added %s entries"%count_s))
            self.stdout.write(self.style.SUCCESS("Updated %s entries"%countedit))
            self.stdout.write(self.style.WARNING("Unable to add %s entries"%count_err))

    def addDay(self,PATH, headerRequired):
        count_s = 0
        count_err = 0
        countedit = 0 

        ignore = ['fig','files','flat','test','bias','panstarrs','bad_flats','reduced','dark','flats','focus','other_objs','fw_test']
        
        targets = [name for name in os.listdir(PATH) if  not name in ignore and isdir(os.path.join(PATH,name))]
        print(targets)

        if len(targets) == 0:
            self.stdout.write(self.style.WARNING('This directory does not contain any images'))
        
        for folder in targets:
            if os.path.exists(os.path.join(PATH,folder,'reduced')):
                url = os.path.join(PATH,folder,'reduced')
            else:
                print("Reduced folder does not exist in ",folder)
                return [count_s, count_err, countedit]
            
            [success,fail,edit] = self.addImages(url, headerRequired)
            
            count_s = count_s + success
            count_err = count_err + fail
            countedit = countedit + edit
        
        
        return [count_s, count_err, countedit]

    def addImages(self,PATH,headerRequired):
        count_s = 0
        count_err = 0
        countedit = 0
        
        images = [name for name in os.listdir(PATH) if name.endswith('-RA.wcs.proc.fits')]
        
        for image in images:
            try:
                if image.count('-RA.wcs.proc')==1:
                    res = self.addImage(os.path.join(PATH,image),headerRequired)
                else:
                    res = 5
            except  Exception as e:
                res = 0
                print('Unable to add filename ', os.path.join(PATH,image))
                print(e)
            
            if res == 0:
                count_err = count_err+1
            elif res == 2:
                count_s = count_s+1
            elif res == 1:
                countedit = countedit+1
            

        return [count_s,count_err,countedit]

    def addImage(self,PATH,headerRequired):

        headers = Image.headers
        cols = headers.keys()
        obj = {}

        header_path = PATH.replace('-RA.wcs.proc.fits','-RA.wcs.proc.header.fits')
        
        if os.path.exists(header_path) and headerRequired:
            obj['header_exists'] = True
            fits = astropy.io.fits.open(header_path)
        else:
            obj['header_exists'] = False
            fits = astropy.io.fits.open(PATH)

        hdu_header = fits[0].header
        fits.close()
        
        obj['filepath'] = os.path.abspath(PATH)
        
        for col in cols:
            # convert and store datetime
            if col=='date_observed':
                warnings.simplefilter("ignore")
                try:
                    datestr = hdu_header[headers[col]]
                except:
                    self.stdout.write(self.style.ERROR("Datetime does not exist in fits file in %s"%PATH))
                    return 0

                try:
                    d = self.parse_prefix(datestr,"%Y-%m-%dT%H:%M:%S.%f")
                    d = pytz.timezone('UTC').localize(d)
                except:
                    try:
                        d = self.parse_prefix(datestr,"%Y-%m-%d %H:%M:%S.%f")
                        d = pytz.timezone('UTC').localize(d)
                    except:
                        try:
                            d = self.parse_prefix(datestr,"%Y-%m-%d%H:%M:%S.%f")
                            d = pytz.timezone('UTC').localize(d)
                        except Exception as e:
                            try:
                                d = self.parse_prefix(datestr,"%Y-%m-%dT%H:%M:%S")
                                d = pytz.timezone('UTC').localize(d)
                            except:
                                try:
                                    d = self.parse_prefix(datestr,"%Y-%m-%d %H:%M:%S")
                                    d = pytz.timezone('UTC').localize(d)
                                except:
                                    try:
                                        d = dateparse.parse_date(datestr)
                                    except:
                                        d = None

                                    if d == None:
                                        self.stdout.write(self.style.ERROR("Unable to add datetime in %s"%PATH))
                                        print(e)
                                        return 0

                obj[col] = d
            else:
                try:
                    obj[col] = hdu_header[headers[col]]
                except:
                    obj[col] = nan
            
        # Healpix        
        try:
            w = wcs.WCS(hdu_header)
        except (KeyError,ValueError):
            w = None
            self.stdout.write(self.style.WARNING("Unable to read WCS for %s"%PATH))
            return 0

        if w!=None:
            try:
                if obj['header_exists']:
                    real_img = astropy.io.fits.open(PATH)
                    real_header = real_img[0].header
                    real_img.close()
                    center_x = real_header['NAXIS1']/2
                    center_y = real_header['NAXIS2']/2
                else:
                    center_x = hdu_header['NAXIS1']/2
                    center_y = hdu_header['NAXIS2']/2
            except:
                try:
                    [head, tail] = os.path.split(PATH)
                    orginal_img_name = tail.split('-RA')[0] + '-RA.fits'
                    orginal_path = os.path.join(head.replace('reduced/',''),orginal_img_name)
                    orginal_img = astropy.io.fits.open(orginal_path)
                    orig_header = orginal_img[0].header
                    orginal_img.close()
                    center_x = orig_header['NAXIS1']/2
                    center_y = orig_header['NAXIS2']/2
                except Exception as e:
                    self.stdout.write(self.style.ERROR(e))
                    print("file name %s"%PATH)
                    return 0
            
            [ra, dec] = w.wcs_pix2world(center_x,center_y,1)
            obj['center_RA'] = ra
            obj['center_Dec'] = dec
            obj['healpy_pxl'] = hp.pixelfunc.ang2pix(settings.N_SIDES,theta=ra,phi=dec,lonlat=True)
            
            # camera
            if center_y*2 == 1472:
                obj['camera'] = 'Apogee'
            elif center_y*2 == 4108:
                obj['camera'] = 'Andor'
            else:
                obj['camera'] = 'SBIG'

        # if difference file exists
        [head, tail] = os.path.split(PATH)
        diff_files = [name for name in os.listdir(head) if name.endswith('.diff')]
        file_name = tail.split('-RA')
        for file in diff_files:
            if file.startswith(file_name[0]):
                obj['diff_exists'] = True
        if obj.get('diff_exists')== None:
            obj['diff_exists'] = False
    

        # obs cycle
        try:
            proposal_params = hdu_header['PROPNUMS'].split('-')
            obj['obs_cycle'] = proposal_params[-2]
        except:
            obj['obs_cycle'] = nan

        try:
            dbimage = Image(**obj)
            record = Image.objects.filter(filepath=obj['filepath']).first()
            if record != None:
                if record==dbimage:
                    return 1
                record.delete()
                dbimage.save()
                return 1
            else:
                dbimage.save()
                return 2
        except Exception as e:
            self.stdout.write(self.style.ERROR("Error adding to database"))
            print(e)
            print(obj['date_observed'])
            print("file name %s"%PATH)
            return 0

    def migrateDataNAS(self,date,newpath):
        images = Image.objects.filter(filepath__contains='/'+date+'/')
        num_images = len(images)
        success = 0
        for image in images:
            try:
                tail = image.filepath.split('/'+date+'/')[1]
                PATH = os.path.join(newpath,date,tail)
                if os.path.exists(PATH):
                    image.filepath = os.path.abspath(PATH)
                    image.save()
                    success += 1
            except:
                print('Unable to update ',image.filepath)
        

        self.stdout.write(self.style.SUCCESS("Updated %s entries"%success))
        self.stdout.write(self.style.ERROR("Unable to update %s entries"%(num_images-success)))
        
    def remakeDB(self, field_name):
        images = Image.objects.all()
        num_images = len(images)
        headers = Image.headers
        success = 0
        
        for image in images:
            try:
                if image.header_exists:
                    header_file_path = image.filepath.replace('-RA.wcs.proc.header.fits','-RA.wcs.proc.fits')
                    fits = astropy.io.fits.open(header_file_path)
                else:
                    fits = astropy.io.fits.open(image.filepath)
                hdu_header = fits[0].header
                fits.close()
                try:
                    newdata = {field_name:hdu_header[headers[field_name]]}
                except:
                    newdata = {field_name:nan}
                Image.objects.filter(pk=image.pk).update(**newdata)
                success += 1
            except Exception as e:
                print(e)
                print('Unable to update ',image.filepath)
        

        self.stdout.write(self.style.SUCCESS("Updated %s entries"%success))
        self.stdout.write(self.style.ERROR("Unable to update %s entries"%(num_images-success)))

    def parse_prefix(self, line, fmt):
        try:
            t = datetime.datetime.strptime(line, fmt)
        except ValueError as v:
            if len(v.args) > 0 and v.args[0].startswith('unconverted data remains: '):
                line = line[:-(len(v.args[0]) - 26)]
                t = datetime.datetime.strptime(line, fmt)
            else:
                raise
        return t
    
    def update_healpxl(self):
        images = Image.objects.all()
        num_images = len(images)
        success = 0
        
        for image in images:
            try:
                # print("{} of {}".format(success,num_images))
                ra = image.center_RA
                dec = image.center_Dec
                newdata = {'healpy_pxl':hp.pixelfunc.ang2pix(settings.N_SIDES,theta=ra,phi=dec,lonlat=True)}
                # Image.objects.filter(pk=image.pk).update(**newdata)
                success += 1
            except:
                try:
                    fits = astropy.io.fits.open(image.filepath)
                    hdu_header = fits[0].header
                    fits.close()
                    try:
                        w = wcs.WCS(hdu_header)
                    except (KeyError,ValueError):
                        w = None
                        self.stdout.write(self.style.WARNING("Unable to read WCS for %s"%image.filepath))
                        continue
                    [ra, dec] = w.wcs_pix2world(image.center_RA,image.center_Dec,1)
                    newdata = {'healpy_pxl':hp.pixelfunc.ang2pix(settings.N_SIDES,theta=ra,phi=dec,lonlat=True)}
                    newdata['center_RA'] = ra
                    newdata['center_Dec'] = dec
                    print("-----------")
                    print("Updated data")
                    print(ra,dec)
                    print("------------")
                    Image.objects.filter(pk=image.pk).update(**newdata)
                    success += 1
                except Exception as e:
                    print(e)
                    print(ra,dec)
                    print('Unable to update ',image.filepath)
            
        
        self.stdout.write(self.style.SUCCESS("Updated %s entries"%success))
        self.stdout.write(self.style.ERROR("Unable to update %s entries"%(num_images-success)))
