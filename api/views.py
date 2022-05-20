from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import ImageSerializer
from dashboard.models import Image
from .filters import ImageFilter
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
from astropy import units as u

@api_view(['GET'])
def getPI(request):
    pass

@api_view(['GET'])
def getPropNums(request):
    pass

@api_view(['GET'])
def getPID(request):
    pass


@api_view(['GET'])
def getData(request):

    query_data = request.query_params
    keys = request.data.keys()

    if query_data.get('ra') != None and query_data.get('dec') != None:
        try:
            ra = float(query_data.get('ra'))
            dec = float(query_data.get('dec'))
            #stage 1
            pxl = hp.pixelfunc.ang2pix(settings.N_SIDES,theta=ra,phi=dec, lonlat=True)
            R = float(query_data.get('radius'))/60 + hp.nside2resol(settings.N_SIDES, arcmin=True) / 60 + settings.HALF_DIAG_FOV
            nearby_pxls = hp.query_disc(nside=settings.N_SIDES,vec=hp.pixelfunc.pix2vec(nside=settings.N_SIDES,ipix=pxl),radius=np.deg2rad(R))
            print("ra-dec ",ra," ",dec)
            print(nearby_pxls)
            query_set = Image.objects.filter(healpy_pxl__in=nearby_pxls)
            #stage 2
            q_ra = np.array([image.center_RA for image in query_set])
            q_dec = np.array([image.center_Dec for image in query_set])
            query_cord = SkyCoord(ra=q_ra*u.degree,dec=q_dec*u.degree)
            tar_cord = SkyCoord(ra=ra,dec=dec,unit='deg')
            sep = tar_cord.separation(query_cord)
            print(sep.degree)
            print(settings.HALF_DIAG_FOV+float(query_data.get('radius'))/60)
            print("-------")
            select_ra = [q_ra[np.where(np.isclose(sep, i))] for i in sep.degree if i<settings.HALF_DIAG_FOV+float(query_data.get('radius'))/60 ]
            select_dec = [q_dec[np.where(np.isclose(sep, i))] for i in sep.degree if i<settings.HALF_DIAG_FOV+float(query_data.get('radius'))/60 ]
            print(select_ra)
            print(select_dec)
            print("------")
            query_set = query_set.filter(center_RA__in=select_ra,center_Dec__in=select_dec)
        except:
            query_set = Image.objects.all()
            pass
    else:
        query_set = Image.objects.all()
    query_set = Image.objects.all()

    if query_data.get('date_after') != None:
        date_after = timezone.datetime.strptime(query_data.get('date_after'),'%Y-%m-%d')
        query_set = Image.objects.filter(date_observed__gte=date_after)
   
    if query_data.get('date_before') != None:
        date_before = timezone.datetime.strptime(query_data.get('date_before'),'%Y-%m-%d')
        date_before = date_before + timedelta(days=1)
        query_set = query_set.filter(date_observed__lte=date_before)

    if len(query_data.getlist('pi[]'))>0:
        query = Q()
        for i in query_data.getlist('pi[]'):
            query |= Q(pi=i)
        query_set = query_set.filter(query)

    if len(query_data.getlist('proposal_no[]'))> 0:
        query = Q()
        for i in query_data.getlist('proposal_no[]'):
            query |= Q(proposal_no=i)
        query_set = query_set.filter(query)

    if len(query_data.getlist('progid[]')) > 0:
        query = Q()
        for i in query_data.getlist('progid[]'):
            query |= Q(progid=i)
        query_set = query_set.filter(query)

    if len(query_data.getlist('filter_used[]'))>0:
        query = Q()
        for i in query_data.getlist('filter_used[]'):
            query |= Q(filter_used=i)
        query_set = query_set.filter(query)


    if len(query_data.getlist('camera[]'))>0:
        query = Q()
        for i in query_data.getlist('camera[]'):
            query |= Q(camera=i)
        query_set = query_set.filter(query)
    

        
    
    # queriedImages = ImageFilter(request.query_params,queryset=query_set)
    print(len(query_set))
    serializer = ImageSerializer(query_set,many=True)

    return Response(serializer.data)