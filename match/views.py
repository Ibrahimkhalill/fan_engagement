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
@permission_classes([IsAdminUser])  # Admin for PUT/DELETE
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
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        match.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



# New API: Filter Live and Upcoming Matches
@api_view(['GET'])
def match_filter(request):
    # Get current date and time in +06 timezone
    tz = timezone.get_fixed_timezone(6 * 60)  # +06:00
    now = datetime.now(tz)
    current_date = now.date()
    current_time = now.time()

    # Define time window for live matches (±15 minutes from start)
    time_window = timedelta(minutes=15)
    match_duration = timedelta(minutes=90)  # Standard match duration
    time_lower = (datetime.combine(datetime.today(), current_time, tzinfo=tz) - time_window).time()
    time_upper = (datetime.combine(datetime.today(), current_time, tzinfo=tz) + time_window).time()

    # Update match statuses
    for match in Match.objects.all():
        match_datetime = datetime.combine(match.date, match.time, tzinfo=tz)
        match_end_datetime = match_datetime + match_duration

        if match.date == current_date and time_lower <= match.time <= time_upper:
            # Match is within ±15 minutes of start time
            if match.status != 'live':
                match.status = 'live'
                match.save(update_fields=['status'])
        elif now >= match_end_datetime:
            # Match has ended (past start time + 90 minutes)
            if match.status != 'finished':
                match.status = 'finished'
                match.save(update_fields=['status'])
        else:
            # Match is upcoming (future date or later today)
            if match.status != 'upcoming':
                match.status = 'upcoming'
                match.save(update_fields=['status'])

    # Filter live and upcoming matches
    live_matches = Match.objects.filter(
        date=current_date,
        time__gte=time_lower,
        time__lte=time_upper,
        status='live'
    ).order_by('date', 'time')

    upcoming_matches = Match.objects.filter(
        models.Q(date__gt=current_date) |
        models.Q(date=current_date, time__gt=time_upper),
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
    # Get current date and time in +06 timezone
    tz = timezone.get_fixed_timezone(6 * 60)  # +06:00
    now = datetime.now(tz)
    current_date = now.date()
    current_time = now.time()

    # Define time window for live matches (±15 minutes from start)
    time_window = timedelta(minutes=15)
    match_duration = timedelta(minutes=90)  # Standard match duration
    time_lower = (datetime.combine(datetime.today(), current_time, tzinfo=tz) - time_window).time()
    time_upper = (datetime.combine(datetime.today(), current_time, tzinfo=tz) + time_window).time()

    # Update match statuses
    for match in Match.objects.all():
        match_datetime = datetime.combine(match.date, match.time, tzinfo=tz)
        match_end_datetime = match_datetime + match_duration

        if match.date == current_date and time_lower <= match.time <= time_upper:
            # Match is within ±15 minutes of start time
            if match.status != 'live':
                match.status = 'live'
                match.save(update_fields=['status'])
        elif now >= match_end_datetime:
            # Match has ended (past start time + 90 minutes)
            if match.status != 'finished':
                match.status = 'finished'
                match.save(update_fields=['status'])
        else:
            # Match is upcoming (future date or later today)
            if match.status != 'upcoming':
                match.status = 'upcoming'
                match.save(update_fields=['status'])

    # Filter live and upcoming matches
    live_matches = Match.objects.filter(
        date=current_date,
        time__gte=time_lower,
        time__lte=time_upper,
        status='live'
    ).order_by('date', 'time')


    # Serialize data
    live_serializer = MatchSerializer(live_matches, many=True)
    

    return Response(
        live_serializer.data,status=status.HTTP_200_OK)


@api_view(['GET'])
def upcoming_match_filter(request):
    # Get current date and time in +06 timezone
    tz = timezone.get_fixed_timezone(6 * 60)  # +06:00
    now = datetime.now(tz)
    current_date = now.date()
    current_time = now.time()

    # Define time window for live matches (±15 minutes from start)
    time_window = timedelta(minutes=15)
    match_duration = timedelta(minutes=90)  # Standard match duration
    time_lower = (datetime.combine(datetime.today(), current_time, tzinfo=tz) - time_window).time()
    time_upper = (datetime.combine(datetime.today(), current_time, tzinfo=tz) + time_window).time()

    # Update match statuses
    for match in Match.objects.all():
        match_datetime = datetime.combine(match.date, match.time, tzinfo=tz)
        match_end_datetime = match_datetime + match_duration

        if match.date == current_date and time_lower <= match.time <= time_upper:
            # Match is within ±15 minutes of start time
            if match.status != 'live':
                match.status = 'live'
                match.save(update_fields=['status'])
        elif now >= match_end_datetime:
            # Match has ended (past start time + 90 minutes)
            if match.status != 'finished':
                match.status = 'finished'
                match.save(update_fields=['status'])
        else:
            # Match is upcoming (future date or later today)
            if match.status != 'upcoming':
                match.status = 'upcoming'
                match.save(update_fields=['status'])

    # Fetch upcoming matches, sorted by date and time (earliest first)
    upcoming_matches = Match.objects.filter(
        models.Q(date__gt=current_date) |
        models.Q(date=current_date, time__gt=time_upper),
        status='upcoming'
    ).order_by('date', 'time')

    # Serialize data
    upcoming_serializer = MatchSerializer(upcoming_matches, many=True)

    return Response(
     
         upcoming_serializer.data
    , status=status.HTTP_200_OK)