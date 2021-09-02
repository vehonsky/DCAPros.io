"""DollarCostAveragePro URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django import contrib
from django.contrib import admin
from django.urls import path, include
from background_task.tasks import Task
from DCAstrategies.tasks import checkOrders, execute_strategies, get_CB_crypto_products, get_strategies_for_execution, updateExecutionCountsandFees

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('DCAstrategies.urls')),
    path('accounts/', include('allauth.urls')),


    #These are all also mapped as apart of running with the path('accounts/', ...) method
    #accounts/ login/ [name='login']
    #accounts/ logout/ [name='logout']
    #accounts/ password_change/ [name='password_change']
    #accounts/ password_change/done/ [name='password_change_done']
    #accounts/ password_reset/ [name='password_reset']
    #accounts/ password_reset/done/ [name='password_reset_done']
    #accounts/ reset/<uidb64>/<token>/ [name='password_reset_confirm']
    #accounts/ reset/done/ [name='password_reset_complete']
]

#Some background tasks to run as soon as the server is loaded
get_CB_crypto_products(repeat=Task.DAILY, repeat_until=None)
get_strategies_for_execution(repeat=300, repeat_until=None)
checkOrders(repeat=300, repeat_until=None)
updateExecutionCountsandFees(repeat=300, repeat_until=None)