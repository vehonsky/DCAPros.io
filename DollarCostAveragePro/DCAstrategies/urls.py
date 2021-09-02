from django.urls import path
from . import views

#List of url patterns that will be rendered
urlpatterns = [
    path('', views.home, name='home'),
    path('make_strategy/', views.make_strategy, name='make_strategy'),
    path('edit_strategy/<uuid:pk>', views.editStrategy, name='edit_strategy'),
    path('strategies/', views.strategies, name='strategies'),
    path('add_api_key/', views.addAPIKey, name='add_api_key'),
    path('edit_api_key/<uuid:pk>', views.editAPIKey, name='edit_api_key'),
    path('delete_api_key/<uuid:pk>', views.deleteAPIKey, name='delete_api_key'),
    path('api_key/', views.APIKey, name='api_key'),
    path('add_payment_method/', views.addPaymentMethod, name='add_payment_method'),
]