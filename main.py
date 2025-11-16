import spotipy
from spotipy.oauth2 import SpotifyOAuth
import lyricsgenius
import os 
import re
import xml.etree.ElementTree as ET
from datetime import datetime, UTC
import html

def build_rss_feed(song_entries, output_file="rss.xml"):
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    # Channel metadata
    ET.SubElement(channel, "title").text = "Cris – Weekly Spotify → Genius Annotated Lyrics"
    ET.SubElement(channel, "link").text = "https://github.com/"
    ET.SubElement(channel, "description").text = (
        "Automatically generated feed of your weekly most-played Spotify tracks with Genius lyric annotations."
    )
    ET.SubElement(channel, "lastBuildDate").text = datetime.now(UTC).strftime("%a, %d %b %Y %H:%M:%S GMT")

    # Add each track as an RSS <item>
    for entry in song_entries:
        item = ET.SubElement(channel, "item")

        ET.SubElement(item, "title").text = f"{entry['track']} – {entry['artist']}"
        ET.SubElement(item, "link").text = entry["genius_url"]

        # Embedded HTML description
        desc = f"""
        <![CDATA[
        <div>
            <img src="{entry['album_art']}" width="200"/>
            <p><b>Track:</b> {html.escape(entry['track'])}</p>
            <p><b>Artist:</b> {html.escape(entry['artist'])}</p>
            <p><a href="{entry['genius_url']}">Open annotated lyrics on Genius</a></p>
        </div>
        ]]>
        """

    # Write XML
    tree = ET.ElementTree(rss)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)

    print(f"RSS feed generated → {output_file}")


def main():

    scope = "user-top-read"
    GENIUS_TOKEN = "cXZIwR1BzX3bDJLBaERELjVJ_i1QEMq5JLlibMdf976IdG_ZKzwqQkgkwgLN6k90"
    SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
    SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
    SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
    SPOTIFY_REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")

    genius = lyricsgenius.Genius(
        GENIUS_TOKEN,
        skip_non_songs=True,
        remove_section_headers=True
        )

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(scope=scope)
    )

    results = sp.current_user_top_tracks(limit=3, time_range="short_term")
    items = results['items']

    # print (items)
    entries = []

    for item in items:
        temp_track = item['name']
        artist = item['artists'][0]['name']

        split_string = re.split(f'[(,)]',temp_track)
        track = split_string[0]
        album_art = item['album']['images'][0]['url']

        url = None
        try:
            genius_result = genius.search_song(track,artist)
            if genius_result:
                url = genius_result.url
        except Exception:
            print(f"No URL found for {track} by {artist}")

        # print(url)
        entries.append({
            "artist":artist,
            "track":track,
            "genius_url":url,
            "album_art":album_art
        })

    # print(entries)
    build_rss_feed(entries)

if __name__ == "__main__":
    main()