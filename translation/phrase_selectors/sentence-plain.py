#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

path_covered   = sys.argv[1]
path_uncovered = sys.argv[2]
file_covered   = open(path_covered)
file_uncovered = open(path_uncovered)

covered = set()
for line in file_covered:
    covered.add(line.strip())
for line in file_uncovered:
    if line.strip() not in covered:
        sys.stdout.write(line)

