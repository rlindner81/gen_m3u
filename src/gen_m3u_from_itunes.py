#!/bin/python

import argparse
import os
import io
import sys

import xml.etree.ElementTree as ET
from os.path import join, isfile
from urlparse import urlparse
from urllib import unquote


def convert_url_to_path(url):
    result = unquote(urlparse(url).path).decode('utf8')
    return result


def get_node_for_key(node, key):
    nodes = iter(node)
    try:
        while True:
            el = nodes.next()
            if el.tag == "key" and el.text == key:
                el = nodes.next()
                if el.tag in ("dict", "array"):
                    return el.getchildren()
                if el.tag in ("string", "integer"):
                    return el.text
                return el
    except StopIteration:
        return None


def get_playlists_from_library_xml(blank_prefix=None):
    library_path = join(os.environ["USERPROFILE"], "Music", "iTunes", "iTunes Music Library.xml")
    if not isfile(library_path):
        print "error: cannot find itunes library xml at {}".format(library_path)
        sys.exit(-1)

    root = ET.parse(library_path).getroot()
    root = iter(root).next()

    tracks = get_node_for_key(root, "Tracks")

    playlists = get_node_for_key(root, "Playlists")
    for playlist in playlists:
        playlist_name = get_node_for_key(playlist, "Name")
        print "processing", playlist_name

        playlist_path = playlist_name + ".m3u"
        playlist_items = get_node_for_key(playlist, "Playlist Items")
        if playlist_items is None:
            print "found not playlist items"
            continue

        track_locations = []
        for playlist_item in playlist_items:
            track_id = get_node_for_key(playlist_item, "Track ID")
            track = get_node_for_key(tracks, track_id)
            track_location = get_node_for_key(track, "Location")
            track_locations.append(track_location)

        track_count = len(track_locations)
        if track_count > 0:
            with io.open(playlist_path, mode="w", encoding="utf8") as fout:
                for track_location in track_locations:
                    track_path = convert_url_to_path(track_location)
                    if blank_prefix and track_path.startswith(blank_prefix):
                        track_path = track_path[len(blank_prefix):]
                    fout.write(u"{}\n".format(track_path))
            print "wrote {} mp3 files into {}".format(track_count, playlist_path)


def get_args():
    parser = argparse.ArgumentParser(description="Generate m3u playlists from iTunes")
    parser.add_argument("--blank-prefix", help="Blank out this prefix in all playlist items")

    return parser.parse_args()


def main():
    args = get_args()

    get_playlists_from_library_xml(blank_prefix=args.blank_prefix)


if __name__ == "__main__":
    main()
