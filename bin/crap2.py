#!/usr/bin/env python

import os
import logging

def getlines(f, o, n):
  with open(f, "r") as infile, open(o, "w") as outfile:
    c = 0
    lines = 0
    logging.warn("skipping until line {}".format(n))
    n = int(n)
    for l in infile:
      c += 1
      if c == n:
        lines += 1
        logging.warn("writing starting at line {}".format(c))
        outfile.write(l)
	for l in infile:
	  lines +=1
	  outfile.write(l)
    logging.warn("wrote {} out of {} lines".format(lines, c))


if __name__ == '__main__':
  import sys
  infile = sys.argv[1]
  outfile = sys.argv[2]
  startline = sys.argv[3]
  getlines(infile, outfile, startline)  

