# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from .models import Player, \
    Station, STATION_TYPE_IMAGES, StationType, \
    Mook, MOOK_TYPE_IMAGES, MookType

import os
import logic

from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client

# Create your views here.

def station_json(station, player):

    if (station.owner == player):
        image_type = 'shiny'
    else:
        image_type = 'normal'

    returnable_json = {
        "position": {"lat": station.lat, "lng": station.lon}, 
        "icon" : STATION_TYPE_IMAGES[StationType(station.station_type)].format(image_type),
        "station_type" : StationType(station.station_type).name ,
        "gathered_energy" : station.gathered_energy,
        "db_id" : station.pk,
        "health" : station.health
        # later, add the callbackOptions
    }

    if station.target:
        returnable_json["target"] = {"lat": station.target.lat, "lng": station.target.lon}

    return returnable_json

def station_locations(request):
    player = None
    if request.user.is_authenticated:
        player = Player.objects.get(user=request.user)
    #if request.user.is_authenticated():
    stations_list = [station_json(station, player) for station in Station.objects.all()]

    return JsonResponse({"data" : stations_list})
    #else:
    #    return HttpResponse("Maybe login first?")

def mook_json(mook, player):

    if (mook.owner == player):
        image_type = 'shiny'
    else:
        image_type = 'normal'

    returnable_json = {
        "position": {"lat": mook.lat, "lng": mook.lon}, 
        "icon" : MOOK_TYPE_IMAGES[MookType(mook.mook_type)].format(image_type),
        "health" : mook.health
    }
    return returnable_json

def mook_locations(request):
    player = None
    if request.user.is_authenticated:
        player = Player.objects.get(user=request.user)

    mook_list = [mook_json(mook, player) for mook in Mook.objects.all()]

    return JsonResponse({"data" : mook_list})

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
def station_collect_energy(request):
    pk = request.POST["pk"]
    lat = float(request.POST["latitude"])
    lon = float(request.POST["longitude"])

    station = Station.objects.get(pk=pk)
    if not logic.within((lat, lon), (station.lat, station.lon), 0.1):
        return JsonResponse({"error" : "Too far from tower."})
    if not request.user.is_authenticated:
        return JsonResponse({"error" : "Unathenticated user."})
    player = Player.objects.get(user=request.user)
    if station.owner != player:
        return JsonResponse({"error" : "Not your tower to collect from."})
        
    station.owner.energy += station.gathered_energy
    station.gathered_energy = 0
    station.owner.save()
    station.save()

    return JsonResponse({
        "station_json" : station_json(station, player), 
        "energy" : get_player_energy(request)
        })

def build_station(request):
    kind = request.POST["kind"]
    lat = float(request.POST["latitude"])
    lon = float(request.POST["longitude"])

    # TODO: add check for nearby towers so towers can't be placed too close together

    if not request.user.is_authenticated:
        return JsonResponse({"error" : "Player not logged in."})

    # make sure they're far enough from other towers.

    if any([
        logic.great_circle_distance(lat, lon, tower.lat, tower.lon) < 0.05
        for tower
        in Station.objects.all()]):
        return JsonResponse({"error" : "Too close to nearby towers."})

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
        "station_json" : station_json(station, player),
        "energy" : get_player_energy(request)})

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

def change_target(request):

    source_pk = request.POST["source"]
    target_pk = request.POST["target"]
    lat = float(request.POST["latitude"])
    lon = float(request.POST["longitude"])

    source = Station.objects.get(pk=source_pk)
    target = Station.objects.get(pk=target_pk)

    if not logic.within((lat, lon), (source.lat, source.lon), 0.1):
        return JsonResponse({"error" : "Too far from tower."})
    if not request.user.is_authenticated:
        return JsonResponse({"error" : "Unathenticated user."})

    player = Player.objects.get(user=request.user)
    if source.owner != player:
        return JsonResponse({"error" : "Not your tower to change target of."})

    source.target = target
    # TODO: change the path too?
    source.save()
    logic.notify(
        source.target.owner,
        "{} just directed an attack towards you! "
        "https://dividedsky.herokuapp.com/".format(
            source.owner.user.username
            )
        )

    response = {
        "path_json" : {
            "position" : {
                "lat" : source.lat,
                "lng" : source.lon
            }, 
            "target" : {
                "lat" : source.target.lat,
                "lng" : source.target.lon
            }
        }
    }
    print(response)

    return JsonResponse(response)

def text_mark(request):
    # Your Account SID from twilio.com/console
    account_sid = "ACff780d521b2eef4ae72b28aafeec12e7"
    # Your Auth Token from twilio.com/console
    auth_token  = os.environ['DIVIDEDSKY_TWILIO_KEY']

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        to="+13095734538", 
        from_="+13093067177",
        body="Hello from Heroku!")

    return HttpResponse(message.sid)