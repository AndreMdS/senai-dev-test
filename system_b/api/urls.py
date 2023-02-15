from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path('auth/', views.AuthView.as_view(), name='auth_user'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('occurrence/<int:occurrence_id>', views.OccurrenceView.as_view(), name='get_occurrence'),
    path('occurrence', views.RegisterOccurrenceView.as_view(), name='post_occurrence'),
    path('occurrences', views.ListOccurrenceView.as_view(), name='list_occurrences'),
]
