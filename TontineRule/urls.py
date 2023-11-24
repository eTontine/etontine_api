from django.urls import path 
from TontineRule.Views.views import *

urlpatterns = [
    path('get-rules/<str:type>', getRules),
    path('add-rule-values', addRuleValues),
    path('get-rule-values/<str:type>/<int:carte_or_groupe_id>', getRuleValues),
]