from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .constants import *
from . import serializers, models
from datetime import datetime

# Create your views here.
class AuthView(APIView):
    @swagger_auto_schema(operation_summary='Authenticate a User',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                USERNAME_LABEL: openapi.Schema(type=openapi.TYPE_STRING, description='User username', example='admin'),
                PASSWORD_LABEL: openapi.Schema(type=openapi.TYPE_STRING, description='User password', example='Senai@2023'),
                }),
        responses={
                status.HTTP_200_OK: 'Authorization token',
                status.HTTP_400_BAD_REQUEST: 'Invalid credentials json data',
            })
    def post(self, request):
        try:
            user_username = request.data[USERNAME_LABEL]
            user_password = request.data[PASSWORD_LABEL]
            user = models.User.objects.get(username=user_username, password=user_password)
        except Exception:
            return Response({'message': 'invalid credentials!'}, status=400)
        refresh = RefreshToken.for_user(user)
        return Response({'refresh': str(refresh), 'access': str(refresh.access_token)}, status=200)

class OccurrenceView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary='GET a Occurrence by Id',
        responses={
            status.HTTP_200_OK: 'Returns the occurrence',
            status.HTTP_404_NOT_FOUND: 'Occurrence not found',
            status.HTTP_401_UNAUTHORIZED: 'Unauthorized',
        },
        manual_parameters=[
            openapi.Parameter(
                name=OCCURRENCE_ID_LABEL,
                type=openapi.TYPE_INTEGER,
                description='The id of occurrence',
                required=True,
                in_=openapi.IN_PATH,
                example=1,
            )])
    def get(self, request, occurrence_id):
        try:
            occurrence = models.Occurrence.objects.get(occurrence_id=occurrence_id)
        except Exception:
            return Response({'message': 'occurrence not found!'}, status=404)
        occurrence_serializer = serializers.OccurrenceSerializer(occurrence)
        return Response(occurrence_serializer.data, status=200)
    
class RegisterOccurrenceView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary='POST a Occurrence',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'mac_address': openapi.Schema(type=openapi.TYPE_STRING, description='Camera MAC Address', example='00:AA:11:BB:22:CC'),
                'object_class': openapi.Schema(type=openapi.TYPE_STRING, description='Object Class', example='mouse'),
                'evidence_url': openapi.Schema(type=openapi.TYPE_STRING, description='Evidence URL', example='file://C:/evidence.jpg'),
                'occurrence_time': openapi.Schema(type=openapi.TYPE_STRING, description='Datetime of Occurrence', example='2023-02-08T00:00:00.000000'),
                }),
        responses={
                status.HTTP_200_OK: 'Occurrence saved',
                status.HTTP_400_BAD_REQUEST: 'Invalid occurrence json data',
                status.HTTP_401_UNAUTHORIZED: 'Unauthorized',
            })
    def post(self, request):
        occurrence_serializer = serializers.OccurrenceSerializer(data=request.data)
        if occurrence_serializer.is_valid():
            occurrence_serializer.save()
            return Response({'message': 'occurrence saved!'}, status=200)
        return Response({'message': 'invalid occurrence json data!'}, status=400)

class ListOccurrenceView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary='List Occurrences in a datetime interval',
        responses={
            status.HTTP_200_OK: 'Returns the list of occurrences',
            status.HTTP_401_UNAUTHORIZED: 'Unauthorized',
        },
        manual_parameters=[
            openapi.Parameter(
                name=QUICK_FILTER_LABEL,
                type=openapi.TYPE_STRING,
                description='A quick filter to set actual year, or month or day datetime interval until now (overrides start_time and end_time)',
                required=False,
                in_=openapi.IN_QUERY,
                enum=[DAY_LABEL, MONTH_LABEL, YEAR_LABEL],
            ),
            openapi.Parameter(
                name=STAR_TIME_LABEL,
                type=openapi.TYPE_STRING,
                description='The start datetime to filter a interval, default is 01/01/2000 at 00:00:00',
                required=False,
                in_=openapi.IN_QUERY,
                example='2023-02-06T00:00:00.000000',
            ),
            openapi.Parameter(
                name=END_TIME_LABEL,
                type=openapi.TYPE_STRING,
                description='The end datetime to filter a interval, default is actual datetime',
                required=False,
                in_=openapi.IN_QUERY,
                example='2023-02-07T00:00:00.000000',
            )])
    def get(self, request):
        start_datetime, end_datetime = self.__get_filter_interval(
            request.query_params.get(STAR_TIME_LABEL),
            request.query_params.get(END_TIME_LABEL),
            request.query_params.get(QUICK_FILTER_LABEL))
        occurrences = models.Occurrence.objects.filter(occurrence_time__range=[start_datetime, end_datetime])
        occurrences_serializer = serializers.OccurrenceSerializer(occurrences, many=True)
        occurrences_list = list(occurrences_serializer.data)
        return Response({'occurrences': occurrences_list, 'total': len(occurrences_list)}, status=200)

    @staticmethod
    def __get_filter_interval(start_time, end_time, quick_filter):
        try:
            start_datetime = datetime.strptime(start_time, DATETIME_FORMAT)
        except Exception:
            start_datetime = datetime(2000, 1, 1)
        
        try:
            end_datetime = datetime.strptime(end_time, DATETIME_FORMAT)
        except Exception:
            end_datetime = datetime.now()
        
        if quick_filter in [DAY_LABEL, MONTH_LABEL, YEAR_LABEL]:
            datetime_now = datetime.now()
            month = 1 if quick_filter == YEAR_LABEL else datetime_now.month
            day = 1 if quick_filter == YEAR_LABEL or quick_filter == MONTH_LABEL else datetime_now.month
            start_datetime = datetime(datetime_now.year, month, day)
        return start_datetime, end_datetime
