#!/usr/bin/env python

##   apply_tokenizer.py

"""
If you have created a new JSON file for the tokenizer, this script is just to test
the tokenizer on a small txt file

Note the following:

1.  Assuming your tokenizer JSON is in the same directory where this script resides, your call
    syntax for this script will look like:

         python3  apply_tokenizer.py   text_sample_for_testing.txt   111_babygpt_tokenizer_50002.json
                                                                     ^^^                   ^^^^^
    Make sure you have changed the number 50002 above to the number in the name of your tokenizer.
    Also, as mentioned elsewhere in the module documentation, the number 111 means that this tokenizer
    was created by Version 1.1.1 of babyGPT


2.  Keep in mind that when you are training a new tokenizer as recommended, it will deposit the 
    tokenizer JSON in a sub-directory with the name 'tokenizer_outputs'.   Along hte same lines, when
    you clean up a tokenizer, the cleaned-up version is deposted in a directory named 
    cleaned_tokenizer_outputs.
"""

from transformers import PreTrainedTokenizerFast

#import itertools
import string
import re
import sys, os
import json
import random


seed_value = 0
random.seed(seed_value)
os.environ['PYTHONHASHSEED'] = str(seed_value)

debug = False

if len(sys.argv) != 3:   
    sys.stderr.write("Usage: %s <textfile name for tokenization>  <tokenizer_json>\n" % sys.argv[0])            
    sys.exit(1)

testing_iter = 0
textfile =  sys.argv[1]
tokenizer_json = sys.argv[2]

tokenizer = PreTrainedTokenizerFast(tokenizer_file=tokenizer_json)

with open( textfile, encoding='utf8', errors='ignore' ) as f: 
    text = f.read()                                           
if debug:
    FILE = open("junk.txt", 'w')
    FILE.write(text)                                                             
    print("\n\nnumber of characters in the file: ", len(text))
    print("The size of the file in bytes: ", os.stat(textfile).st_size)
    FILE.chose()

print("\n\nTHE ORIGINAL TEXT: : ", text)

encoded = tokenizer.encode(text, add_special_tokens=False) 

print("\n\nENCODED INTO INTEGERS: ", encoded)

decoded = tokenizer.decode(encoded, skip_special_tokens=True)

print("\n\nDECODED SYMBOLIC TOKENS FROM THE INTEGERS: ", decoded)

