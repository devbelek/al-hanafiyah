from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import QuestionViewSet

router = DefaultRouter()
router.register(r'questions', QuestionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]