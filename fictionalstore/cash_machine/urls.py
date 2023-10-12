from django.urls import path

from cash_machine import views

urlpatterns = [
    path('cash_machine', views.CashMachineApi.as_view())
]

