#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
from collections import defaultdict

THRESHOLD=2

debugging = True
def dprint(msg):
    if debugging:
        print(msg)

if len(sys.argv) != 3:
    sys.stderr.write("Usage: %s base_sentences additional_trees > phrases\n" % sys.argv[0])
    sys.exit(1)

base_sent_file = open(sys.argv[1])
add_struct_file = open(sys.argv[2])

word2id = {}
id2word = []
def getWord(num):
    if 0 <= num and num < len(id2word):
        return id2word[num]
    return "-UNK-"
def getID(word):
    if word not in word2id:
        word2id[word] = len(id2word)
        id2word.append(word)
    return word2id[word]
def getPhrase(idvec):
    return str.join(' ', map(getWord, idvec))
def getIDVec(phrase):
    if type(phrase) == str:
        return tuple( map(getID, phrase.split()) )
    return tuple( map(getID, phrase) )

def parse(expr, i = 0):
    cont = ''
    while i < len(expr):
        #dprint('Expr[%s]: %s' % (i, expr[i]))
        if expr[i] == '(':
            #dprint('Push')
            cont = []
            while i < len(expr):
                if expr[i] == ')':
                    #dprint("Closing: %s" % cont)
                    return cont, i + 1
                item, i = parse(expr, i + 1)
                if item:
                    #print("Appending: %s" % item)
                    cont.append(item)
            return cont, i
        elif expr[i] == ')':
            #dprint("Closing: " + cont)
            return cont, i
        elif expr[i] == ' ':
            #dprint('Elem: ' + cont)
            return cont, i
        else:
            cont += expr[i]
            i += 1
    return cont, i

def extractPhrase(tree):
    words = ()
    if type(tree) == list:
        for elem in tree[1:None]:
            words += extractPhrase(elem)
    else:
        words += (getID(tree),)
    return words

def countPhrases(tree, counter = defaultdict(int), sentence = ""):
    global covered
    if type(tree) == list:
        if len(tree) >= 3:
            words = extractPhrase(tree)
            #print(words)
            if getPhrase(words) not in covered:
                if words not in counter:
                    counter[words] = [1, sentence]
                else:
                    counter[words][0] += 1
        for elem in tree[1:None]:
            countPhrases(elem, counter, sentence)
    else:
        #print(getIDVec(tree))
        words = getIDVec(tree)
        if getPhrase(words) not in covered:
            if words not in counter:
                counter[words] = [1, sentence]
            else:
                counter[words][0] += 1

def get_ngram_phrases(sent, n = 4):
    words = sent.strip().split(' ')
    for i in range(1, n+1):
        for left in range(0, len(words)+1-i):
            yield str.join(' ', words[left:left+i])

covered = set()
for line in base_sent_file:
    for phrase in get_ngram_phrases(line):
        covered.add(phrase)
#counter = defaultdict(int)
counter = dict()
#for line in sys.stdin:
for line in add_struct_file:
    line = line.strip()
    tree, _ = parse(line)
    if tree:
        sentence = getPhrase(extractPhrase(tree))
        #sentence = line.replace('(', '').replace(')', '')
        #sentence = re.sub(r' +', ' ', sentence)
        countPhrases(tree, counter, sentence)

#for line in base_sent_file:
#    to_remove = []
#    for key in counter.keys():
#        phrase = getPhrase(key)
#        if line.find(phrase) >= 0:
#            to_remove.append(key)
#    if to_remove:
#        for key in to_remove:
#            del counter[key]

key_func = lambda key: (-counter[key][0], len(key))
#for key in counter.keys():
for key in sorted(counter.keys(), key=key_func):
    count = counter[key][0]
    if count >= THRESHOLD:
        phrase = getPhrase(key)
        context = counter[key][1]
        count = counter[key][0]
        sys.stdout.write("%s\t%s\t%s\n" % (phrase, context, count))
        #print("%s\t%s" % (getPhrase(key),count))

