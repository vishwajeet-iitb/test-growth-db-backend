from typing import ValuesView
from django.urls import path
from . import views

urlpatterns = [
    path('images',views.getData),
    path('pi',views.getPI),
    path('propnums',views.getPropNums),
    path('pid',views.getPID),
]
