from django.shortcuts import render, redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import  Advertisement
from .serializers import  AdvertisementSerializer


# Advertisement Views
@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def advertisement_list_create(request):
    if request.method == 'GET':
        advertisements = Advertisement.objects.all()
        serializer = AdvertisementSerializer(advertisements, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Delete all existing advertisements before creating a new one
        Advertisement.objects.all().delete()

        serializer = AdvertisementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# New View: Latest Advertisement for Authenticated Users
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def advertisement_list_for_user(request):
    if request.method == 'GET':
        advertisement = Advertisement.objects.order_by('-created_at').first()  # Get latest ad
        if advertisement:
            serializer = AdvertisementSerializer(advertisement)
            return Response(serializer.data)
        return Response({"detail": "No advertisements available"}, status=status.HTTP_404_NOT_FOUND)
    
  

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def advertisement_detail(request, pk):
    try:
        advertisement = Advertisement.objects.get(pk=pk)
    except Advertisement.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = AdvertisementSerializer(advertisement)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = AdvertisementSerializer(advertisement, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        advertisement.delete()
        return Response({"messages": "Advertise deleted sucessfully"},status=status.HTTP_204_NO_CONTENT)



