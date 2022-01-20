from genericpath import isdir
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
        parser.add_argument('--header',help='Add custom header (-RA.wcs.proc.header.fits) files rather than default')

    def handle(self, *args, **options):
        counts = 0
        counte = 0
        countedit = 0
        
        add = options['add']
        edit = options['edit']
        folder = options['dir']
        day = options['day']
        bulk = options['i']
        headerfile = options['header']

        if headerfile=='True':
            headerfile = True
        elif headerfile=='False':
            headerfile = False
        else:
            self.stdout.write(self.style.ERROR("Unknown argument for header"))
            return

        if add != None and folder == None and day == None and bulk == None and edit == None:
            if not os.path.exists(add):
                self.stdout.write(self.style.ERROR("Path does not exist"))
                return
            res = self.addImage(add)
            if res == 0:
                counte = counte+1
            elif res == 2:
                counts = counts+1
            elif res == 1:
                countedit = countedit+1
        elif add == None and folder != None and day == None and bulk == None and edit == None:
            if not os.path.exists(folder):
                self.stdout.write(self.style.ERROR("Path does not exist"))
                return
            [counts,counte,countedit] = self.addImages(folder,headerfile)   
        elif add == None and folder == None and day != None and bulk == None and edit == None:
            if not os.path.exists(day):
                self.stdout.write(self.style.ERROR("Path does not exist"))
                return
            [counts,counte, countedit] = self.addDay(day,headerfile)
        elif add == None and folder == None and day == None and bulk != None and edit == None:
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
                        counts = counts + success
                        counte = counte + fail
                        countedit = countedit + edit
                    else:
                        self.stdout.write(self.style.WARNING("Folder of %s does not exists"%name))

                    start = start + datetime.timedelta(days=1)
                
        elif add == None and folder == None and day == None and bulk == None and edit != None:
            res = self.editImage(edit)
            if res == 0:
                counte = counte+1
            elif res == 2:
                counts = counts+1
            elif res == 1:
                countedit = countedit+1

        self.stdout.write(self.style.SUCCESS("Added %s entries"%counts))
        self.stdout.write(self.style.SUCCESS("Updated %s entries"%countedit))
        self.stdout.write(self.style.WARNING("Unable to add %s entries"%counte))

    def addDay(self,PATH,h):
        counts = 0
        counte = 0
        countedit = 0 
        ignore = ['fig','files','flat','test','bias']
        targets = [name for name in os.listdir(PATH) if  not name in ignore and isdir(os.path.join(PATH,name))]
        print(targets)
        for folder in targets:
            if os.path.exists(os.path.join(PATH,folder,'reduced')):
                url = os.path.join(PATH,folder,'reduced')
            else:
                print("Reduced folder does not exist in ",folder)
                return [counts, counte, countedit]
            [success,fail,edit] = self.addImages(url, h)
            counts = counts + success
            counte = counte + fail
            countedit = countedit + edit
        return [counts, counte, countedit]

    def addImages(self,PATH, h):
        counts = 0
        counte = 0
        countedit = 0
        extension_name = '-RA.wcs.proc.fits' if not h else '-RA.wcs.proc.header.fits'
        images = [name for name in os.listdir(PATH) if name.endswith(extension_name)]
        for image in images:
            res = self.addImage(os.path.join(PATH,image))
            if res == 0:
                counte = counte+1
            elif res == 2:
                counts = counts+1
            elif res == 1:
                countedit = countedit+1
            

        return [counts,counte,countedit]

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
        obj['filepath'] = os.path.abspath(PATH)
        try:
            dbimage = Image(**obj)
            record = Image.objects.filter(filepath=os.path.abspath(PATH))
            if record.exists():
                record = dbimage
                record.save()
                return 1
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

