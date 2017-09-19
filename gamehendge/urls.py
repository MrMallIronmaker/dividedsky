from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^station_locations/$', views.station_locations, name='station_locations'),
    url(r'^$', views.map, name='map'),
    url(r'^move_mooks_good/$', views.move_mooks_webpage, name='movingmooksgreatagain'),
    url(r'^station_collect_energy/$', views.station_collect_energy),
    url(r'^build_station/$', views.build_station),
    #url(r'^credit_energy/$', views.credit_energy) # this is a function for adding 1 to energy
]