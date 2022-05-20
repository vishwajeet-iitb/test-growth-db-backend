from typing import ValuesView
from django.urls import path
from . import views
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView)

urlpatterns = [
    path('images',views.getData),
    path('pi',views.getPI),
    path('propnums',views.getPropNums),
    path('pid',views.getPID),
    path('api-token/', TokenObtainPairView.as_view()),
    path('api-token-refresh/', TokenRefreshView.as_view()),
]
