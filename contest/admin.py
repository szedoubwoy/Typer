from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import Match, Bet

# Rozszerzenie istniejącej klasy UserAdmin
class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ('username', 'email', 'is_staff', 'is_active',)
    list_filter = ('is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                    'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_active', 'is_staff')}
        ),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

# Zarejestruj rozszerzoną klasę admina
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('home_team', 'away_team', 'date', 'actual_home_team_score', 'actual_away_team_score', 'final_score')
    list_filter = ('group', 'date')
    search_fields = ('home_team', 'away_team', 'place')
    list_editable = ('actual_home_team_score', 'actual_away_team_score', 'final_score')

@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ('user', 'match', 'home_team_score', 'away_team_score', 'created_at')
    list_filter = ('user', 'match')
    search_fields = ('user__username', 'match__home_team', 'match__away_team')