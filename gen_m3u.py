#!/bin/python

import argparse
import os
import io
import sys
import fnmatch
from mutagen.mp3 import MP3

ARTIST_TAGS = ("TPE2", "TPE1")
TITLE_TAGS = ("TIT2",)
TRACKNUMBER_TAGS = ("TRCK", "TPOS")


def normalize_dir():
    script_dir = os.path.dirname(sys.argv[0])
    if script_dir:
        os.chdir(script_dir)


def gen_all_m3u(musicpath):
    print "processing",
    playlist_path = os.path.join("all.m3u")
    track_count = 0
    with io.open(playlist_path, mode="w", encoding="utf8") as fout:
        fout.write(u"#EXTM3U\n")
        for path, dirnames, filenames in os.walk(unicode(musicpath)):
            sys.stdout.write(".")
            track_infos = []
            for filename in fnmatch.filter(filenames, "*.mp3"):
                track_path = os.path.join(path, filename)

                mp3_data = MP3(track_path)

                track_infos.append({
                    "path": track_path,
                    "length": int(mp3_data.info.length),
                    "artist": get_tag_text(mp3_data, ARTIST_TAGS, "Artist"),
                    "title": get_tag_text(mp3_data, TITLE_TAGS, "Title"),
                    "tracknumber": get_tracknumber(mp3_data)
                })

            for track_info in sorted(track_infos, key=lambda x: x["tracknumber"]):
                fout.write(u"#EXTINF:{},{} - {}\n".format(track_info["length"], track_info["artist"], track_info["title"]))
                fout.write(track_info["path"] + "\n")
                track_count += 1
    print "\nwrote {} tracks to {}".format(track_count, playlist_path)


def get_tag_text(mp3_data, check_tags, fallback):
    mp3_tags = mp3_data.tags
    for tag in check_tags:
        if tag in mp3_tags:
            return mp3_tags[tag].text[0]
    return fallback


def get_tracknumber(mp3_data):
    number = get_tag_text(mp3_data, TRACKNUMBER_TAGS, None)
    if number is None:
        return sys.maxint

    if "/" in number:
        return int(number[:number.find("/")])

    return int(number)


def get_args():
    parser = argparse.ArgumentParser(description='Generate m3u playlists')
    parser.add_argument("mp3_dir", help="Directory with mp3 files")

    return parser.parse_args()


def main():
    args = get_args()
    gen_m3u(args.mp3_dir)


if __name__ == "__main__":
    main()
