import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TRCK
import re
import requests
import sys

# Get spotify credentials
def authenticate():
	try:
		with open('creds.txt', 'r') as file:
			c = json.load(file)
	except FileNotFoundError:
		print("[!] ERROR: creds.txt file not found. Must be in same directory")
		sys.exit(1)
	except json.JSONDecodeError as e:
		print("[!] ERROR: creds.txt is not formatted correctly")
		sys.exit(1)

	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=c.get('client_id'),
                                               client_secret=c.get('client_secret'),
                                               redirect_uri=c.get('redirect_uri'),
                                               scope='playlist-read-private'))
	return sp, c.get('username')

# Download audio from given url and write to filename
def download_audio(url, filename):
    r = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(r.content)

# Get all tracks in a playlist
def get_tracks(sp, username, playlist_id):
    results = sp.user_playlist_tracks(username, playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

def add_metadata(filename, track_name, artist, album_name, track_num, album_art):
	audio = MP3(filename, ID3=ID3)
	audio.tags = ID3()

	audio.tags.add(TIT2(encoding=3, text=track_name))
	audio.tags.add(TPE1(encoding=3, text=artist))
	audio.tags.add(TALB(encoding=3, text=album_name)) 
	audio.tags.add(TRCK(encoding=3, text=str(track_num)))

	response = requests.get(album_art)
	if response.status_code == 200:
		image_data = response.content
		image = APIC(
                encoding=3,
                mime="image/jpeg",
                type=3,
                desc="Album Art",
                data=image_data
				)
		audio.tags.add(image)
	
	audio.save()

# Iterate through playlist, gather metadata, and download audio
def get_playlist(sp, username, playlist_id):
	playlist = get_tracks(sp, username, playlist_id)
	for track in playlist:
		print(json.dumps(track, indent = 4))
		track_name = track['track']['name']
		artist = track['track']['artists'][0]['name']
		album_name = track['track']['album']['name']
		track_num = track['track']['track_number']
		album_art = track['track']['album']['images'][0]['url']
		audio_url = track['track']['preview_url']
		if audio_url:
			filename = f"{track_name}.mp3"
			download_audio(audio_url, filename)
			add_metadata(filename, track_name, artist, album_name, track_num, album_art)
			print(f"Downloaded {filename}")

def main():
	if len(sys.argv) < 2:
		print("[!] ERROR: usage: python spotify2mp3.py <playlist_url>")
		sys.exit(1)
	sp, username = authenticate()

	playlist_url = sys.argv[1]
	playlist_id = re.search(r'playlist/([^/?]+)', playlist_url).group(1)
	get_playlist(sp, username, playlist_id)

if __name__ == "__main__":
    main()
