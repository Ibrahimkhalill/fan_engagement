from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser  # Corrected to IsAdminUser
from .models import Player
from .serializers import PlayerSerializer

# Player Views
@api_view(['GET', 'POST'])
def player_list_create(request):
    if request.method == 'GET':
        players = Player.objects.all()
        serializer = PlayerSerializer(players, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PlayerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])  # Admin for PUT/DELETE
def player_detail(request, pk):
    try:
        player = Player.objects.get(pk=pk)
    except Player.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = PlayerSerializer(player)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = PlayerSerializer(player, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        player.delete()
        return Response({"messages":"Player deleted successfully"},status=status.HTTP_204_NO_CONTENT)