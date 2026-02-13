from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TradeViewSet, CapitalInvestmentPlanViewSet

app_name = 'investments'

router = DefaultRouter()
router.register(r'trades', TradeViewSet, basename='trade')
router.register(r'investment-plans', CapitalInvestmentPlanViewSet, basename='investment-plan')

urlpatterns = [
    path('', include(router.urls)),
]
