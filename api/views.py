from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import ImageSerializer
from dashboard.models import Image

@api_view(['GET'])
def getData(request):

    query_data = request.query_params
    keys = request.data.keys()
    print(query_data)
    print(keys)

    # kwargs = {}
    # for key in keys:
        
    #     if query_data[key] != '' and query_data[key] != None :
    #         kwargs[key] = query_data[key]

    queriedImages = Image.objects.all()

    if query_data.get('tar_name') != None:
        if query_data.get('exact') == None:
            pass #Raise error
        elif query_data.get('exact'):
            queriedImages = queriedImages.filter(tar_name=query_data['tar_name'])
        else:
            queriedImages = queriedImages.filter(tar_name__contains=query_data['tar_name'])
    
    if query_data.get('pi') != None:
        queriedImages = queriedImages.filter(pi__in=query_data['pi'])

    if query_data.get('proposal_no') != None:
        queriedImages = queriedImages.filter(proposal_no__in=query_data['proposal_no']) 

    if query_data.get('progid') != None:
        queriedImages = queriedImages.filter(progid__in=query_data['progid']) 

    serializer = ImageSerializer(queriedImages,many=True)

    # data = {"Hello":"World"}
    return Response(serializer.data)