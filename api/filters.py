from dashboard.models import Image
import django_filters
from django.db.models import Q

class ImageFilter(django_filters.FilterSet):
    
    sidereal = django_filters.BooleanFilter(method="sidereal_query")    
    tar_name = django_filters.CharFilter(field_name="tar_name")
    tar_name_match = django_filters.CharFilter(field_name="tar_name",lookup_expr="icontains")


    #main properties
    tel_alt = django_filters.RangeFilter(field_name="tel_alt")
    ha = django_filters.RangeFilter(field_name="ha")
    tel_az = django_filters.RangeFilter(field_name="tel_az")
    fwhm = django_filters.RangeFilter(field_name="fwhm")
    lim_mag3 = django_filters.RangeFilter(field_name="lim_mag3")
    lim_mag5 = django_filters.RangeFilter(field_name="lim_mag5")
    # psf_zp = django_filters.RangeFilter(field_name="psf_zp")

    #secondary properites
    # img_sub = django_filters.BooleanFilter(field_name="diff_exists")

    # obs_tile = django_filters.BooleanFilter(method="is_obs_tile")
    # psf_type = django_filters.BooleanFilter(field_name="psf_type")



    air_mass = django_filters.RangeFilter(field_name="air_mass")
    avg = django_filters.RangeFilter(field_name="avg")
    ccd_temp = django_filters.RangeFilter(field_name="ccd_temp")
    epsf_mag = django_filters.RangeFilter(field_name="psf_merr")
    epsf_zp = django_filters.RangeFilter(field_name="psf_zerr")
    exptime = django_filters.RangeFilter(field_name="exptime")
    psf_mag = django_filters.RangeFilter(field_name="psf_mag")
    psf_zp = django_filters.RangeFilter(field_name="psf_zp")
    stdev = django_filters.RangeFilter(field_name="stdev")


    class Meta:
        model = Image
        exclude = ['healpy_pxl','header_exists']

    
    def sidereal_query(self,queryset,name,value):
        if value:
            query1 = Q(ra_rate__gt=0)
            query2 = Q(dec_rate__gt=0)
            queryset = queryset.filter(query1&query2)
        return queryset

    def is_obs_tile(self,queryset,name,value):
        if value:
            query = Q(tile_id__gt=0)
            queryset = queryset.filter(query)
        return queryset

    def date_query(self,queryset,name,value):
        if value:
            print(len(queryset))
            query = Q(date_observed=value)
            queryset = queryset.filter(query)
            print(len(queryset))
        return queryset