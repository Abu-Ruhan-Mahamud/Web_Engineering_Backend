from django.urls import path
from . import views

urlpatterns = [
    path("lab-tests/", views.lab_test_list, name="lab-test-list"),
    path("lab-tests/<int:pk>/", views.lab_test_detail, name="lab-test-detail"),
    path(
        "lab-tests/<int:pk>/result/",
        views.lab_test_result,
        name="lab-test-result",
    ),
    path(
        "lab-tests/<int:pk>/result/update/",
        views.lab_test_result_update,
        name="lab-test-result-update",
    ),
]
