# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from .models import Station, STATION_TYPE_IMAGES, StationType, Player

import logic

from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def station_json(station):
    return {
        "position": {"lat": station.lat, "lng": station.lon}, 
        "icon" : STATION_TYPE_IMAGES[StationType(station.station_type)] ,
        "station_type" : StationType(station.station_type).name ,
        "gathered_energy" : station.gathered_energy,
        "db_id" : station.pk
        # later, add the callbackOptions
    }

def station_locations(request):
    #if request.user.is_authenticated():
    stations_list = [station_json(station) for station in Station.objects.all()]

    return JsonResponse({"data" : stations_list})
    #else:
    #    return HttpResponse("Maybe login first?")

def get_player_energy(request):
    if request.user.is_authenticated:
        player = Player.objects.get(user=request.user)
        energy = player.energy
    else:
        energy = "Not logged in."

    return energy

def map(request):
    return render(request, 'gamehendge/map.html', context={"energy" : get_player_energy(request)})

def move_mooks_webpage(request):
    return HttpResponse(logic.move_mooks())


# TODO: should these calls be csrf_exempt?
@csrf_exempt
def station_collect_energy(request):
    pk = request.POST["pk"]
    lat = request.POST["latitude"]
    lon = request.POST["longitude"]

    station = Station.objects.get(pk=pk)
    if not logic.within((lat, lon), (station.lat, station.lon), 0.1):
        return JsonResponse({"error" : "Too far from tower."})
    if not request.user.is_authenticated:
        return JsonResponse({"error" : "Unathenticated user."})
    if station.owner != Player.objects.get(user=request.user):
        return JsonResponse({"error" : "Not your tower to collect from."})
        
    station.owner.energy += station.gathered_energy
    station.gathered_energy = 0
    station.owner.save()
    station.save()

    return JsonResponse({
        "station_json" : station_json(station), 
        "energy" : get_player_energy(request)
        })

@csrf_exempt
def build_station(request):
    kind = request.POST["kind"]
    lat = request.POST["latitude"]
    lon = request.POST["longitude"]

    # TODO: add check for nearby towers so towers can't be placed too close together

    if not request.user.is_authenticated:
        return JsonResponse({"error" : "Player not logged in."})

    # check if there's enough energy for them to build their tower
    # TODO: make this a database type? not sure how to do this.
    if kind == 'lightning':
        price = 15
    else:
        price = 10

    player = Player.objects.get(user=request.user)
    if (player.energy < price):
        return JsonResponse({"error" : "Insufficient energy to buy tower."})

    # charge the player
    player.energy -= price

    # build the tower
    station = Station(
        station_type=StationType[kind].value,
        team=player.team,
        lat=lat, lon=lon,
        owner=player,
    )

    # save
    station.save()
    player.save()

    return JsonResponse({
        "station_json" : station_json(station),
        "energy" : get_player_energy(request)})

def credit_energy(request):
    logic.credit_energy()
    return HttpResponse("Success.")

@csrf_exempt
def delete_station(request):
    pk = request.POST["pk"]

    station = Station.objects.get(pk=pk)
    if not request.user.is_authenticated:
        return JsonResponse({"error" : "Unathenticated user."})

    if station.owner != Player.objects.get(user=request.user):
        return JsonResponse({"error" : "Not your tower to delete."})

    # TODO: fix this magic number
    station.owner.energy += 6
    station.owner.save()
    station.delete()

    return JsonResponse({"energy" : get_player_energy(request)})