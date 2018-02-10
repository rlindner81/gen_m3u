#!/bin/python

import argparse
import os
import io
import sys
import fnmatch

from os.path import split, isdir, abspath


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


def get_args():
    parser = argparse.ArgumentParser(description='Generate m3u playlists')
    parser.add_argument("--dir", help="Directory with mp3 files (default=all subdirectories)")

    return parser.parse_args()


def main():
    args = get_args()
    if args.dir:
        gen_m3u_for_dir(args.dir)
    else:
        for mp3_dir in filter(lambda x: isdir(x), os.listdir(os.getcwd())):
            gen_m3u_for_dir(mp3_dir)


if __name__ == "__main__":
    main()
