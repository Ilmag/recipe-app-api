"""
URL mappings for the recipe app.
"""
from django.urls import ( # noqa
    path, # noqa
    include, # noqa
)

from rest_framework.routers import DefaultRouter # noqa

from recipe import views # noqa


router = DefaultRouter()
router.register('recipes', views.RecipeViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
]
