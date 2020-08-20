#!/bin/python
import argparse
import io
import re
from difflib import SequenceMatcher

leading_numbers_and_trailing_mp3_re = re.compile(r'^(?:[-\d]+|)\s*(.*?)\s*(?:.mp3|)$')


def fuzzy_search(content, separator='\n'):
    originals = content.split(separator)
    shorts = [x[x.rfind('/') + 1:] for x in originals]
    shorts = [leading_numbers_and_trailing_mp3_re.sub(r'\1', x) for x in shorts]
    n = len(shorts)
    for i in range(n):
        left = shorts[i]
        for j in range(n):
            if j == i: continue
            right = shorts[j]
            ratio = SequenceMatcher(None, left, right).ratio()
            if ratio > 0.8:
                print('\n'.join(('match with %0.3f' % ratio, originals[i], originals[j])), '\n')


def get_args():
    parser = argparse.ArgumentParser(description='Find fuzzy matches within m3u lists')
    parser.add_argument('filename', help='playlist file to look through')
    return parser.parse_args()


def main():
    args = get_args()
    with io.open(args.filename, "r") as fin:
        fuzzy_search(fin.read())


if __name__ == "__main__":
    main()
