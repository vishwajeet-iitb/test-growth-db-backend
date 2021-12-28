from math import nan
from django.core.management.base import BaseCommand
from dashboard.models import Image
import datetime, pytz
import os, warnings
import astropy.io.fits

class Command(BaseCommand):

    def add_arguments(self, parser) :
        parser.add_argument('--add',help="Add a single image from a path")
        parser.add_argument('--edit',help="Edit a single image from a path")
        parser.add_argument('--dir',help="Add images from a path")
        parser.add_argument('--day',help="Add all images from a day")
        parser.add_argument('-i', nargs=3, help="Find folders of days and add them. Provide path, startdate, enddate in the format yyyymmdd")

    def handle(self, *args, **options):
        counts = 0
        counte = 0
        
        add = options['add']
        edit = options['edit']
        folder = options['dir']
        day = options['day']
        bulk = options['i']

        if add != None and folder == None and day == None and bulk == None and edit == None:
            res = self.addImage(add)
            if res == 0:
                counte = counte+1
            elif res == 2:
                counts = counts+1
        elif add == None and folder != None and day == None and bulk == None and edit == None:
            [counts,counte] = self.addImages(folder)   
        elif add == None and folder == None and day != None and bulk == None and edit == None:
            [counts,counte] = self.addDay(day)
        elif add == None and folder == None and day == None and bulk != None and edit == None:
            # import all data
            day1 = bulk[1]
            day2 = bulk[2]
            PATH = bulk[0]
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
                        [success,fail] = self.addDay(os.path.join(PATH,name))
                        counts = counts + success
                        counte = counte + fail
                    else:
                        self.stdout.write(self.style.WARNING("Folder of %s does not exists"%name))

                    start = start + datetime.timedelta(days=1)
                
        elif add == None and folder == None and day == None and bulk == None and edit != None:
            res = self.editImage(edit)
            if res == 0:
                counte = counte+1
            elif res == 2:
                counts = counts+1

        self.stdout.write(self.style.SUCCESS("Added %s entries"%counts))
        self.stdout.write(self.style.WARNING("Unable to add %s entries"%counte))

    def addDay(self,PATH):
        counts = 0
        counte = 0
        ignore = ['fig','files','flat','test','bias']
        targets = [name for name in os.listdir(PATH) if os.path.exists(os.path.join(PATH,name,'reduced')) and not name in ignore]
        print(targets)
        for folder in targets:
            url = os.path.join(PATH,folder,'reduced')
            [success,fail] = self.addImages(url)
            counts = counts + success
            counte = counte + fail
        return [counts,counte]

    def addImages(self,PATH):
        counts = 0
        counte = 0
        headers = Image.headers
        cols = headers.keys()
        images = [name for name in os.listdir(PATH) if name.endswith('-RA.wcs.proc.fits')]
        for image in images:
            res = self.addImage(os.path.join(PATH,image))
            if res == 0:
                counte = counte+1
            elif res == 2:
                counts = counts+1
            

        return [counts,counte]

    def addImage(self,PATH):
        if Image.objects.filter(filepath=PATH):
            return 1
        headers = Image.headers
        cols = headers.keys()
        fits = astropy.io.fits.open(PATH)
        hdu = fits[0]
        obj = {}
        for col in cols:
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
        obj['filepath'] = PATH
        try:
            dbimage = Image(**obj)
            if Image.objects.filter(filepath=PATH):
                record = Image.objects.filter(filepath=PATH)
                record = dbimage
                record.save()
            else:
                dbimage.save()
            return 2
        except Exception as e:
            self.stdout.write(self.style.ERROR("Error adding to database"))
            print(e)
            print("file name %s"%PATH)
            return 0

    def editImage(self,PATH):
        headers = Image.headers
        cols = headers.keys()
        fits = astropy.io.fits.open(PATH)
        hdu = fits[0]
        obj = {}
        for col in cols:
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
        obj['filepath'] = PATH
        try:

            if Image.objects.filter(filepath=PATH):
                dbimage = Image(**obj)
                record = Image.objects.filter(filepath=PATH)
                record = dbimage
                record.save()
                dbimage.save()
            else:
                self.stdout.write(self.style.ERROR("Record does not exist, Did you mean add?"))
            return 2
        except Exception as e:
            self.stdout.write(self.style.ERROR("Unable to edit"))
            print(e)
            print("file name %s"%PATH)
            clash = Image.objects.filter(jd=obj['jd'])
            for i in clash:
                print(i.filepath)
            return 0

