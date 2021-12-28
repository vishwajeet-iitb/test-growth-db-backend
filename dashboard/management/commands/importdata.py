from math import exp, nan
from django.core.management.base import BaseCommand
from dashboard.models import Image
import datetime, pytz
import os
import astropy.io.fits

class Command(BaseCommand):

    def handle(self, *args, **options):
        counts = 0
        counte = 0
        headers = Image.headers
        cols = headers.keys()
        ignore = ['fig','files','flat','test','bias']
        PATH = '/home/adithya/iSURP/data/20211124'
        targets = [name for name in os.listdir(PATH) if os.path.exists(os.path.join(PATH,name,'reduced')) and not name in ignore]
        print(targets)
        for folder in targets:
            url = os.path.join(PATH,folder,'reduced')
            images = [name for name in os.listdir(url) if name.endswith('-RA.wcs.proc.fits')]

            for image in images:
                fits = astropy.io.fits.open(os.path.join(url,image))
                hdu = fits[0]
                obj = {}
                for col in cols:
                    if col=='date_observed':
                        try:
                            d = datetime.datetime.strptime(hdu.header[headers[col]], "%Y-%m-%dT%H:%M:%S.%f" )
                        except:
                            try:
                                d = datetime.datetime.strptime(hdu.header[headers[col]], "%Y-%m-%d %H:%M:%S.%f" )
                            except:
                                pass

                        print(d)
                        d = pytz.timezone('UTC').localize(d)
                        print(d)
                        obj[col] = d
                    try:
                        obj[col] = hdu.header[headers[col]]
                    except:
                        obj[col] = nan
                obj['filepath'] = os.path.join(url,image)
                try:
                    dbimage = Image(**obj)
                    dbimage.save()
                    counts=counts+1
                except Exception as e:
                    print("Error adding to database")
                    print(e)
                    print("file name %s"%image)
                    counte=counte+1
        
        self.stdout.write(self.style.SUCCESS("Added %s entries"%counts))
        self.stdout.write(self.style.WARNING("Unable to add %s entries"%counte))