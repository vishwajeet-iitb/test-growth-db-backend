from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import ImageSerializer
from dashboard.models import Image
from .filters import ImageFilter
from django.db.models import Q

import numpy as np
import healpy as hp

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
            pxl = hp.pixelfunc.ang2pix(settings.N_SIDES,theta=np.deg2rad(dec),phi=np.deg2rad(ra), lonlat=True)
            R = float(query_data.get('radius'))/60 + hp.nside2resol(settings.N_SIDES, arcmin=True) / 60 + settings.HALF_DIAG_FOV
            nearby_pxls = hp.query_disc(nside=settings.N_SIDES,vec=hp.pixelfunc.pix2vec(nside=settings.N_SIDES,ipix=pxl),radius=np.deg2rad(R))
            print("ra-dec ",ra," ",dec)
            print(nearby_pxls)
            query_set = Image.objects.filter(healpy_pxl__in=nearby_pxls)
        except:
            query_set = Image.objects.all()
            pass
    else:
        query_set = Image.objects.all()
    
    
    
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
        
    
    queriedImages = ImageFilter(request.query_params,queryset=query_set)
    print(len(queriedImages.qs))
    serializer = ImageSerializer(queriedImages.qs,many=True)

    return Response(serializer.data)