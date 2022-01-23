from email.headerregistry import HeaderRegistry
from genericpath import isdir
from math import nan
from django.core.management.base import BaseCommand
from dashboard.models import Image
import datetime, pytz
import os, warnings
import astropy.io.fits
import numpy as np
import healpy as hp
import astropy.wcs as wcs

class Command(BaseCommand):

    def add_arguments(self, parser) :
        parser.add_argument('--add',help="Add a single image from a path")
        parser.add_argument('--edit',help="Edit a single image from a path")
        parser.add_argument('--dir',help="Add images from a path")
        parser.add_argument('--day',help="Add all images from a day")
        parser.add_argument('-i', nargs=3, help="Find folders of days and add them. Provide path, startdate, enddate in the format yyyymmdd")
        parser.add_argument('--header',help='Add custom header (-RA.wcs.proc.header.fits) files rather than default')
        parser.add_argument('--migrate', nargs=2 ,help='Migrate file path to NAS. Inputs - date in format yyyymmdd and new path including the folder name')
    

    def handle(self, *args, **options):
        count_s = 0
        count_err = 0
        countedit = 0
        
        add = options['add']
        folder = options['dir']
        day = options['day']
        bulk = options['i']
        headerfile = options['header']
        migrateData = options['migrate']

        if headerfile != None:
            if headerfile=='True':
                headerfile = True
            elif headerfile=='False':
                headerfile = False
            else:
                self.stdout.write(self.style.ERROR("Unknown argument for --header"))
                return
        else:
            headerfile = False
        

        if add != None and folder == None and day == None and bulk == None and migrateData == None:
            if not os.path.exists(add):
                self.stdout.write(self.style.ERROR("Path does not exist"))
                return
            res = self.addImage(add)
            if res == 0:
                count_err = count_err+1
            elif res == 2:
                count_s = count_s+1
            elif res == 1:
                countedit = countedit+1
        elif add == None and folder != None and day == None and bulk == None and migrateData == None:
            if not os.path.exists(folder):
                self.stdout.write(self.style.ERROR("Path does not exist"))
                return
            [count_s,count_err,countedit] = self.addImages(folder,headerfile)   
        elif add == None and folder == None and day != None and bulk == None and migrateData == None:
            if not os.path.exists(day):
                self.stdout.write(self.style.ERROR("Path does not exist"))
                return
            [count_s,count_err, countedit] = self.addDay(day,headerfile)
        elif add == None and folder == None and day == None and bulk != None and migrateData == None:
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
                        [success,fail,edit] = self.addDay(os.path.join(PATH,name),headerfile)
                        count_s = count_s + success
                        count_err = count_err + fail
                        countedit = countedit + edit
                    else:
                        self.stdout.write(self.style.WARNING("Folder of %s does not exists"%name))

                    start = start + datetime.timedelta(days=1)
                
        elif add == None and folder == None and day == None and bulk == None and migrateData != None:
            self.migrateDataNAS(migrateData[0],migrateData[1])

        if migrateData == None:
            self.stdout.write(self.style.SUCCESS("Added %s entries"%count_s))
            self.stdout.write(self.style.SUCCESS("Updated %s entries"%countedit))
            self.stdout.write(self.style.WARNING("Unable to add %s entries"%count_err))

    def addDay(self,PATH,h):
        count_s = 0
        count_err = 0
        countedit = 0 
        ignore = ['fig','files','flat','test','bias']
        targets = [name for name in os.listdir(PATH) if  not name in ignore and isdir(os.path.join(PATH,name))]
        print(targets)
        for folder in targets:
            if os.path.exists(os.path.join(PATH,folder,'reduced')):
                url = os.path.join(PATH,folder,'reduced')
            else:
                print("Reduced folder does not exist in ",folder)
                return [count_s, count_err, countedit]
            [success,fail,edit] = self.addImages(url, h)
            count_s = count_s + success
            count_err = count_err + fail
            countedit = countedit + edit
        return [count_s, count_err, countedit]

    def addImages(self,PATH, h):
        count_s = 0
        count_err = 0
        countedit = 0
        extension_name = '-RA.wcs.proc.fits' if not h else '-RA.wcs.proc.header.fits'
        images = [name for name in os.listdir(PATH) if name.endswith(extension_name)]
        for image in images:
            res = self.addImage(os.path.join(PATH,image),h)
            if res == 0:
                count_err = count_err+1
            elif res == 2:
                count_s = count_s+1
            elif res == 1:
                countedit = countedit+1
            

        return [count_s,count_err,countedit]

    def addImage(self,PATH,h):
        NSIDE = 64 # for healpix

        headers = Image.headers
        cols = headers.keys()
        fits = astropy.io.fits.open(PATH)
        hdu = fits[0]
        obj = {}
        for col in cols:
            # convert and store datetime
            if col=='date_observed':
                warnings.simplefilter("ignore")
                try:
                    d = datetime.datetime.strptime(hdu.header[headers[col]], "%Y-%m-%dT%H:%M:%S.%f" )
                except:
                    try:
                        d = datetime.datetime.strptime(hdu.header[headers[col]], "%Y-%m-%d %H:%M:%S.%f" )
                    except:
                        pass

                d = pytz.timezone('UTC').localize(d)
                obj[col] = d
            try:
                obj[col] = hdu.header[headers[col]]
            except:
                obj[col] = nan

        # Healpix        
        try:
            w = wcs.WCS(hdu.header)
        except (KeyError,ValueError):
            w = None
            self.stdout.write(self.style.WARNING("Unable to read WCS for %s"%PATH))

        if w!=None:
            try:
                center_x = hdu.header['NAXIS1']/2
                center_y = hdu.header['NAXIS2']/2
                [ra, dec] = w.wcs_pix2world(center_x,center_y,1)
                obj['healpy_pxl'] = hp.pixelfunc.ang2pix(NSIDE,theta=np.deg2rad(dec),phi=np.deg2rad(ra), lonlat=True)
            except Exception as e:
                self.stdout.write(self.style.ERROR(e))
                print("file name %s"%PATH)
        # if difference file exists
        [head, tail] = os.path.split(PATH)
        diff_files = [name for name in os.listdir(head) if name.endswith('.diff')]
        file_name = tail.split('-RA')
        for file in diff_files:
            if file.startswith(file_name[0]):
                obj['diff_exists'] = 'yes'
        if obj.get('diff_exists')== None:
            obj['diff_exists'] = 'no'

        # for special header files
        if h:
            [head, tail] = os.path.split(PATH)
            new_file_name = tail.replace('-RA.wcs.proc.header.fits','-RA.wcs.proc.fits')
            new_path = os.path.join(head,new_file_name)
            if os.path.exists(new_path):
                obj['filepath'] = os.path.abspath(new_path)
            else:
                self.stdout.write(self.style.ERROR("Image file does not exist for %s"%PATH))
                return 0
        else:
            obj['filepath'] = os.path.abspath(PATH)
        try:
            dbimage = Image(**obj)
            record = Image.objects.filter(filepath=os.path.abspath(PATH))
            if record.exists():
                record.delete()
                dbimage.save()
                return 1
            else:
                dbimage.save()
                return 2
        except Exception as e:
            self.stdout.write(self.style.ERROR("Error adding to database"))
            print(e)
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
                pass
        

        self.stdout.write(self.style.SUCCESS("Updated %s entries"%success))
        self.stdout.write(self.style.ERROR("Unable to update %s entries"%(num_images-success)))
        