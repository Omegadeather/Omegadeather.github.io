from django.contrib import admin
from django.urls import path, include

from . import views
from .views import SignUpView

urlpatterns = [
    # path('admin/', admin.site.urls),

    path('signup/', SignUpView.as_view(), name="signup"),
    path('loginn/', views.loginn, name='loginn'),
    path('callback/', views.callback, name='callback'),
    path('refresh_token/', views.refresh_token, name='refresh_token'),
    path('spotify/playlists/', views.get_spotify_playlists, name='spotify_playlists'),
    path('link-success/', views.link_spotify_success, name='link_spotify_success'),
    path('wrappost/', views.wrappost, name='wrappost'),
    path('delete/', views.delete, name='delete'),
    path('game/', views.song_guessing_game, name='song_guessing_game'),
    path('password_change/', views.password_change, name='password_change'),
    path('past_wraps/', views.past_wraps, name='past_wraps'),
    path('save_spotify_wrap/', views.save_spotify_wrap, name='save_spotify_wrap'),
    path('contact/', views.contact, name='contact'),
    path('wrap/<int:wrap_id>/', views.wrap_detail, name='wrap_detail'),

]
