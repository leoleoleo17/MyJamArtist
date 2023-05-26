import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def get_artist_genres(artist_name):
    # Set up Spotipy client credentials
    client_id = '4417bca2fc0f405aa211b519e067bbaf'
    client_secret = '9d53090efda44e968a6d4d5f5166ca36'
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Search for the artist
    results = sp.search(q=artist_name, type='artist', limit=1)
    if 'artists' in results and 'items' in results['artists'] and len(results['artists']['items']) > 0:
        artist = results['artists']['items'][0]
        return artist['genres']
    else:
        return []


# Get the genres for the artist
genres = get_artist_genres('Standing On the Corner')

# Print the genres
if len(genres) > 0:
    print("Genres for 'Standing On the Corner':")
    for genre in genres:
        print(genre)
else:
    print("No genres found for this artist.")
