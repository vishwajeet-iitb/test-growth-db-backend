from typing import ValuesView
from django.urls import path
from . import views
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView)

urlpatterns = [
    path('images',views.ImageView.as_view()),
    path('pi',views.PIView.as_view()),
    path('propnums',views.PropNumsView.as_view()),
    path('pid',views.PIDView.as_view()),
    path('api-token/', TokenObtainPairView.as_view()),
    path('api-token-refresh/', TokenRefreshView.as_view()),
]
