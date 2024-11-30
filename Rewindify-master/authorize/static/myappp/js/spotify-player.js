// Ensure the Spotify Web Playback SDK script is included before this script runs
// This can be done in your user_info.html file or your base.html

// Add this function in your script
window.onSpotifyWebPlaybackSDKReady = () => {
    const token = '{{ access_token }}'; // Ensure you get the token correctly
    const player = new Spotify.Player({
        name: 'Web Playback SDK',
        getOAuthToken: cb => { cb(token); },
        volume: 0.5
    });

    // Connect to the player!
    player.connect();

    // You can add additional event listeners for player state changes here
    player.addListener('initialization_error', ({ message }) => { console.error(message); });
    player.addListener('authentication_error', ({ message }) => { console.error(message); });
    player.addListener('account_error', ({ message }) => { console.error(message); });
    player.addListener('playback_error', ({ message }) => { console.error(message); });

    // Other player events (like player state changes) can be added here
};
