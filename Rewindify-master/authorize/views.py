from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic

from django.http import HttpResponse
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.shortcuts import redirect, render
import requests
import json
import base64
from spotipy.oauth2 import SpotifyOAuth
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from .models import SpotifyWrap  # Ensure this import is present

from .forms import CustomUserCreationForm
#from .models import UserSpotifyProfile, Wrap
import logging
import base64
import json
import random
import string
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.models import Session
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .forms import CustomPasswordChangeForm

import openai


# Spotify API and app credentials
CLIENT_ID = settings.SPOTIFY_CLIENT_ID
CLIENT_SECRET = settings.SPOTIFY_CLIENT_SECRET
REDIRECT_URI = settings.SPOTIFY_REDIRECT_URI
STATE_KEY = 'spotify_auth_state'
openai.api_key = settings.OPENAI_API_KEY  # Make sure you set this in your settings.py

def create_music_profile_description(top_artists, genres):
    artist_names = [artist['name'] for artist in top_artists['items']]
    genre_names = list(genres)

    prompt = f"""
    Based on the following music preferences, describe the personality, fashion, and behavior traits of someone who listens to this kind of music:

    Top Artists: {', '.join(artist_names)}
    Top Genres: {', '.join(genre_names)}

    The person enjoys these musical styles. What are they like in terms of personality, fashion choices, and what might their hobbies or interests be? Write the prompt in second person
    """
    return prompt

def get_music_description(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or "gpt-4"
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.7,
    )
    description = response.choices[0].message['content'].strip()
    return description




def generate_random_string(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def loginn(request):
    # Generate a random state string to prevent CSRF attacks
    state = generate_random_string()
    request.session[STATE_KEY] = state

    # Spotify authorization URL
    scope = 'user-read-private user-read-email user-top-read user-library-read'
    auth_url = f'https://accounts.spotify.com/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&state={state}&scope={scope}'

    return redirect(auth_url)

def callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')

    if not code:
        return HttpResponse("No authorization code received", status=400)

    # Exchange the authorization code for an access token
    auth = (settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET)
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    token_url = 'https://accounts.spotify.com/api/token'
    response = requests.post(token_url, data=data, headers=headers, auth=auth)

    if response.status_code != 200:
        return HttpResponse("Error fetching token", status=500)

    token_data = response.json()
    access_token = token_data.get('access_token')

    if not access_token:
        return HttpResponse("Failed to retrieve access token", status=500)

    # Save access token to session
    request.session['spotify_token'] = access_token

    # Fetch user profile data from Spotify
    user_profile_url = 'https://api.spotify.com/v1/me'
    user_profile_headers = {
        'Authorization': f'Bearer {access_token}',
    }
    user_profile_response = requests.get(user_profile_url, headers=user_profile_headers)

    if user_profile_response.status_code != 200:
        return HttpResponse("Error fetching user profile", status=500)

    user_profile = user_profile_response.json()


    # Extract the display name and profile picture URL
    display_name = user_profile.get('display_name', '')
    profile_picture = None
    if 'images' in user_profile and len(user_profile['images']) > 0:
        profile_picture = user_profile['images'][0].get('url', None)

    # Fetch playlists
    sp = spotipy.Spotify(auth=access_token)
    playlists = sp.current_user_playlists()
    top_tracks = sp.current_user_top_tracks(limit=5)
    top_artists = sp.current_user_top_artists(limit=5)
    total_minutes = 0  # Variable to store total listening time in minutes

    genres = set()  # Using a set to avoid duplicates
    for artist in top_artists['items']:
        artist_info = sp.artist(artist['id'])  # Get detailed artist information
        genres.update(artist_info['genres'])

    music_description_prompt = create_music_profile_description(top_artists, genres)
    music_description = get_music_description(music_description_prompt)


    top_tracks = sp.current_user_top_tracks(limit=5)
    top_tracks_with_previews = []

    for track in top_tracks['items']:
        preview_url = track['preview_url']  # Spotify provides 30-second preview URL
        top_tracks_with_previews.append({
            'name': track['name'],
            'artists': [artist['name'] for artist in track['artists']],
            'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None,
            'preview_url': preview_url
        })

    for track in top_tracks['items']:
        track_duration_ms = track['duration_ms']
        total_minutes += track_duration_ms / 60000

    top_artists_with_images = []
    for artist in top_artists['items']:
        artist_name = artist['name']
        artist_image = artist['images'][0]['url'] if artist['images'] else None
        top_artists_with_images.append({
            'name': artist_name,
            'image': artist_image
        })

    playlists_with_images = []
    for playlist in playlists['items']:
        playlist_name = playlist['name']
        playlist_image = playlist['images'][0]['url'] if playlist['images'] else None
        playlists_with_images.append({
            'name': playlist_name,
            'image': playlist_image
        })

    # Check if the form was submitted to save the data
    spotify_wrap = SpotifyWrap(
        user=request.user,
        top_tracks=top_tracks_with_previews,
        top_artists=top_artists_with_images,
        top_genres=list(genres),
        total_minutes=round(total_minutes, 2),
        playlists=playlists_with_images,
        music_description=music_description,

        display_name=display_name,  # Save display name
        profile_picture=profile_picture  # Save profile picture URL
    )
    spotify_wrap.save()

    messages.success(request, "Your Spotify wrap has been saved!")


        # Pass the list of top tracks with previews to the template
    return render(request, 'registration/logged_in.html', {
        'profile': user_profile,
        'playlists': playlists['items'],
        'top_tracks': top_tracks_with_previews,
        'top_artists': top_artists['items'],
        'genres': list(genres) if genres else None,
        'total_minutes': round(total_minutes, 2) if total_minutes else None,
        'music_description': music_description,  # Send the description generated by the LLM

    })
@csrf_exempt
def refresh_token(request):
    refresh_token = request.POST.get('refresh_token')

    # Prepare token refresh request
    token_url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode('utf-8'),
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }

    response = requests.post(token_url, headers=headers, data=data)

    if response.status_code == 200:
        tokens = response.json()
        return JsonResponse(tokens)
    else:
        return JsonResponse({'error': 'failed_to_refresh_token'}, status=400)


def get_spotify_playlists(request):
    access_token = request.session.get('spotify_token')
    if not access_token:
        return redirect('spotify_login')  # Redirect to login if token is missing

    sp = spotipy.Spotify(auth=access_token)
    playlists = sp.current_user_playlists()

    return render(request, 'registration/show_playlists.html', {'playlists': playlists['items']})

def save_spotify_wrap(request):
    if request.method == 'POST':
        # Assuming `request.user` is the logged-in user
        spotify_wrap = SpotifyWrap(
            user=request.user,
            top_tracks=request.POST.get('top_tracks', []),  # This should come from your form
            top_artists=request.POST.get('top_artists', []),  # This should come from your form
            top_genres=request.POST.get('top_genres', []),    # This should come from your form
            total_minutes=request.POST.get('total_minutes', 0), # Similarly, retrieve the data you want
            playlists=request.POST.get('playlists', [])
        )
        spotify_wrap.save()
        return HttpResponse('Spotify wrap saved successfully!')

    return redirect('home')


class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


def link_spotify_success(request):
    return render(request, 'registration/link_spotify_success.html')

def wrappost(request):
    return render(request, 'registration/wrap_post.html')

@login_required
def delete(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('home')  # Redirect to home page or login page after account deletion

    return render(request, 'registration/delete.html')

def password_change(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            # Update the session to keep the user logged in after password change
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('home')  # Redirect to a page after successful password change
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'registration/password_change.html', {'form': form})

@login_required
def delete(request):
    if request.method == "POST":
        user = request.user
        user.delete()
        messages.success(request, "Your account has been deleted successfully.")
        return redirect("home")  # Redirect to the homepage or login page after deletion

    return render(request, "registration/delete.html")


@login_required
def past_wraps(request):
    wraps = SpotifyWrap.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "registration/past_wraps.html", {"wraps": wraps})

def wrap_detail(request, wrap_id):
    wrap = get_object_or_404(SpotifyWrap, id=wrap_id)  # Fetch a specific wrap by ID
    return render(request, 'registration/wrap_detail.html', {'wrap': wrap})

@login_required
def song_guessing_game(request):
    access_token = request.session.get('spotify_token')
    if not access_token:
        messages.success(request, "You have not generated any wraps yet. Redirecting...")
        return redirect('loginn')

    sp = spotipy.Spotify(auth=access_token)
    top_tracks = sp.current_user_top_tracks(limit=10)
    if not top_tracks['items']:
        return render(request, 'registration/song_guessing_game.html')

    def prepare_game_data():
        correct_track = random.choice(top_tracks['items'])
        correct_track_data = {
            'track_name': correct_track['name'],
            'track_preview_url': correct_track['preview_url'],
            'track_artist': ", ".join([artist['name'] for artist in correct_track['artists']]),
            'track_album_image': correct_track['album']['images'][0]['url'] if correct_track['album']['images'] else None
        }
        options = [correct_track]
        while len(options) < 4:
            random_track = random.choice(top_tracks['items'])
            if random_track not in options:
                options.append(random_track)
        random.shuffle(options)
        options_data = [{
            'track_name': track['name'],
            'track_artist': ", ".join([artist['name'] for artist in track['artists']]),
            'track_album_image': track['album']['images'][0]['url'] if track['album']['images'] else None
        } for track in options]
        return correct_track_data, options_data

    if 'correct_track' not in request.session or request.method == 'GET':
        correct_track_data, options_data = prepare_game_data()
        request.session['correct_track'] = correct_track_data
        request.session['options'] = options_data

    correct_track_data = request.session['correct_track']
    options_data = request.session['options']
    feedback = None

    if request.method == 'POST':
        user_guess = request.POST.get('user_guess').strip()
        correct_answer = correct_track_data['track_name'].strip()
        if user_guess.lower() == correct_answer.lower():
            feedback = "Correct! You guessed the right song."
            correct_track_data, options_data = prepare_game_data()
            request.session['correct_track'] = correct_track_data
            request.session['options'] = options_data
        else:
            feedback = f"Incorrect! The correct answer was '{correct_answer}'."

    return render(request, 'registration/song_guessing_game.html', {
        **correct_track_data,
        'options': options_data,
        'feedback': feedback
    })

def contact(request):

    return render(request, 'registration/contact.html')
