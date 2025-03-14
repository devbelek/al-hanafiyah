from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'telegram', 'is_ustaz']
    search_fields = ['user__username', 'user__email', 'telegram']
    list_filter = ['is_ustaz']