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
    if type(tree) == list:
        if len(tree) >= 3:
            words = extractPhrase(tree)
            #print(words)
            if words not in counter:
                counter[words] = [1, sentence]
            else:
                counter[words][0] += 1
        for elem in tree[1:None]:
            countPhrases(elem, counter, sentence)
    else:
        #print(getIDVec(tree))
        counter[getIDVec(tree)] += 1

#counter = defaultdict(int)
counter = dict()
#for line in sys.stdin:
for line in add_struct_file:
    line = line.strip()
    tree, _ = parse(line)
    #print(tree)
    if tree:
        sentence = line.replace('(', '').replace(')', '')
        sentence = re.sub(r' +', ' ', sentence)
        countPhrases(tree, counter, sentence)

for key in counter.keys():
    count = counter[key][0]
    if count >= THRESHOLD:
        phrase = getPhrase(key)
        context = counter[key][1]
        count = counter[key][0]
        print("%s\t%s\t%s\n" % (phrase, context, count))
        #print("%s\t%s" % (getPhrase(key),count))

