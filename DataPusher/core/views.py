from django.shortcuts import render

from rest_framework import viewsets
from .models import Account, Destination
from .serializers import AccountSerializer, DestinationSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
import requests

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer

@api_view(['GET'])
def get_destinations(request, account_id):
    try:
        account = Account.objects.get(account_id=account_id)
        destinations = account.destinations.all()
        serializer = DestinationSerializer(destinations, many=True)
        return Response(serializer.data)
    except Account.DoesNotExist:
        return Response({"error": "Account not found"}, status=404)

@api_view(['POST'])
def incoming_data(request):
    app_secret_token = request.headers.get('CL-X-TOKEN')
    if not app_secret_token:
        return JsonResponse({"error": "Authentication token missinge"}, status=401)

    try:
        account = Account.objects.get(app_secret_token=app_secret_token)
    except Account.DoesNotExist:
        return JsonResponse({"error": "Invalid authentication token"}, status=401)

    data = request.data
    if request.method == 'POST' and not isinstance(data, dict):
        return JsonResponse({"error": "Invalid data format"}, status=400)

    for destination in account.destinations.all():
        headers = destination.headers
        method = destination.http_method
        url = destination.url
        try:
            if method == 'GET':
                response = requests.get(url, params=data, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"status": "Success"})

@api_view(['POST'])
def create_account(request):
    serializer = AccountSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

