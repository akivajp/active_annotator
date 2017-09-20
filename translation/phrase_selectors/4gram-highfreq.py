#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

N = 4

path_covered   = sys.argv[1]
path_uncovered = sys.argv[2]
file_covered   = open(path_covered)
file_uncovered = open(path_uncovered)

def get_ngram_phrases(sent, n = N):
    words = sent.strip().split(' ')
    for i in range(1, n+1):
        for left in range(0, len(words)+1-i):
            yield str.join(' ', words[left:left+i])

covered = set()
for line in file_covered:
    for phrase in get_ngram_phrases(line):
        covered.add(phrase)
# storing: phrase -> [count, context]
phrase_counts = dict()
for line in file_uncovered:
    for phrase in get_ngram_phrases(line):
        if phrase not in covered:
            if phrase not in phrase_counts:
                phrase_counts[phrase] = [1, line.strip()]
            else:
                phrase_counts[phrase][0] += 1

# ignoring phrases with 1 occurence count
candidates = list()
for phrase in phrase_counts.keys():
    if phrase_counts[phrase][0] > 1:
        candidates.append(phrase)
#compare_count = lambda p1, p2: phrase_counts[p1][0] > phrase_counts[p2][0]
#for phrase in sorted(candidates, cmp=compare_count):
key_func = lambda p: (-phrase_counts[p][0], len(p))
for phrase in sorted(candidates, key=key_func):
    count, context = phrase_counts[phrase]
    sys.stdout.write("%s\t%s\t%s\n" % (phrase, context, count))

