#!/bin/python

import argparse
import os
import io
import sys
import fnmatch

import xml.etree.ElementTree as ET
from os.path import join, split, isdir, isfile, abspath


def gen_m3u_for_dir(mp3_dir, playlist_name=None):
    print "processing directory {}...".format(mp3_dir)
    mp3_count = 0
    mp3_paths = []

    if not isdir(mp3_dir):
        print "error: {} is not a directory".format(mp3_dir)
        sys.exit(-1)

    if playlist_name is None:
        playlist_name = split(abspath(mp3_dir))[-1]
    playlist_path = playlist_name + ".m3u"

    for path, dirnames, filenames in os.walk(unicode(mp3_dir)):
        for filename in fnmatch.filter(filenames, "*.mp3"):
            mp3_path = os.path.join(path, filename)
            mp3_paths.append(mp3_path)
            mp3_count += 1

    if len(mp3_paths) == 0:
        print "found no mp3 files"
        return

    with io.open(playlist_path, mode="w", encoding="utf8") as fout:
        for mp3_path in mp3_paths:
            fout.write(mp3_path + "\n")
    print "wrote {} mp3 files into {}".format(mp3_count, playlist_path)


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


def get_playlists_from_library_xml():
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
                    fout.write(u"{}\n".format(track_location))
            print "wrote {} mp3 files into {}".format(track_count, playlist_path)


def get_args():
    parser = argparse.ArgumentParser(description='Generate m3u playlists from iTunes')
    parser.add_argument("dir", help="iTunes Directory")

    return parser.parse_args()


def main():
    args = get_args()

    get_playlists_from_library_xml()


if __name__ == "__main__":
    main()
