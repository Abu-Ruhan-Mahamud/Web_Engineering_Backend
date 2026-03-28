from django.urls import path
from . import views

urlpatterns = [
    path("documents/", views.document_list, name="document-list"),
    path("documents/<int:pk>/", views.document_detail, name="document-detail"),
]
