import imp
from pyexpat import model
from rest_framework import serializers
from dashboard.models import Image
from userlogin.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
    
    
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'
