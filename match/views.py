from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser  # Corrected to IsAdminUser
from .models import  Match
from .serializers import  MatchSerializer
from datetime import datetime, time, timedelta
from django.utils import timezone
from django.db import models
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Match Views
@api_view(['GET', 'POST'])
def match_list_create(request):
    if request.method == 'GET':
        matches = Match.objects.all()
        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        print("data", request.data)
        serializer = MatchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
# @permission_classes([IsAdminUser])  # Admin for PUT/DELETE
def match_detail(request, pk):
    try:
        match = Match.objects.get(pk=pk)
    except Match.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = MatchSerializer(match)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = MatchSerializer(match, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            group_name = "match_status_all"
            channel_layer = get_channel_layer()

            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "match_status_update",
                    "match_id": match.id,
                }
            )    
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        match.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



# New API: Filter Live and Upcoming Matches
@api_view(['GET'])
def match_filter(request):


    # Filter live and upcoming matches
    live_matches = Match.objects.filter(
        status='live'
    ).order_by('date', 'time')

    upcoming_matches = Match.objects.filter(
        status='upcoming'
    ).order_by('date', 'time')

    # Serialize data
    live_serializer = MatchSerializer(live_matches, many=True)
    upcoming_serializer = MatchSerializer(upcoming_matches, many=True)

    return Response({
        'live_matches': live_serializer.data,
        'upcoming_matches': upcoming_serializer.data
    })


@api_view(['GET'])
def live_match_filter(request):

    # Filter live and upcoming matches
    live_matches = Match.objects.filter(
        status='live'
    ).order_by('date', 'time')

    # Serialize data
    live_serializer = MatchSerializer(live_matches, many=True)
    
    return Response(
        live_serializer.data,status=status.HTTP_200_OK)


@api_view(['GET'])
def upcoming_match_filter(request):
   
    # Fetch upcoming matches, sorted by date and time (earliest first)
    upcoming_matches = Match.objects.filter(
       
        status='upcoming'
    ).order_by('date', 'time')

    # Serialize data
    upcoming_serializer = MatchSerializer(upcoming_matches, many=True)

    return Response(
     
         upcoming_serializer.data
    , status=status.HTTP_200_OK)