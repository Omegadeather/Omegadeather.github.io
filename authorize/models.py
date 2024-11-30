from django.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField
from django.utils import timezone
from django.utils.timezone import now

from django.db import models
from django.contrib.auth.models import User

class SpotifyWrap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    top_tracks = models.JSONField()  # Store top tracks as JSON data
    top_artists = models.JSONField()  # Store top artists as JSON data
    top_genres = models.JSONField()  # Store genres as JSON data
    total_minutes = models.FloatField()  # Store total minutes of listening
    playlists = models.JSONField()  # Store playlists as JSON data
    music_description = models.TextField()  # Store music description as text
    created_at = models.DateTimeField(auto_now_add=True)

    display_name = models.CharField(max_length=255, blank=True, null=True)  # Store display name
    profile_picture = models.URLField(blank=True, null=True)  # Store profile picture URL


    def __str__(self):
        return f"Spotify Wrap for {self.user.username} - {self.created_at}"


class UserSpotifyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    spotify_id = models.CharField(max_length=255, unique=True)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    profile = models.ForeignKey(SpotifyWrap, on_delete=models.CASCADE, related_name='user_data')

    def __str__(self):
        return self.user.username

