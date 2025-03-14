from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import CategoryViewSet, TopicViewSet, ModuleViewSet, LessonViewSet, UstazProfileViewSet

router = DefaultRouter()
router.register(r'ustaz-profile', UstazProfileViewSet, basename='ustaz-profile')
router.register(r'categories', CategoryViewSet)
router.register(r'topics', TopicViewSet)
router.register(r'modules', ModuleViewSet)
router.register(r'lessons', LessonViewSet)

urlpatterns = [
    path('', include(router.urls)),
]