#!/usr/bin/env python
# coding: utf-8

import os
import sys
import xml.etree.ElementTree as ET
from multiprocessing import Pool
import xml_converter_lib
import time

'''
INSTRUCTIONS
-------------------------------------------------------------------
This is a converter script to convert Pascal VOC .xml annotation 
files to Darknet .txt annotation files.

Put both xml_converter.py and xml_converter_lib.py in the dir 
above the folder containing the annotations in Pascal VOC format.

Put labels.txt in the dir above xml_converter.py.

If you want to change where the text files are written to, modify 
def write_converted_file() in xml_converter_lib.py.

Default write location is <subdir>/txt.

Uses multiprocessing to spawn multiple threads for minor speed-up.
Run main(<your_chosen_num_threads>) if you run into problems.
'''

def main(num_threads = xml_converter_lib.getThreads()):

    subdir = input("Enter subdir: ")

    start = time.time()
    p = Pool(processes = num_threads)
    files = xml_converter_lib.FileGenerator(subdir)()
    p.map(xml_converter_lib.write_converted_file, files)
    p.close()
    p.join()
    end = time.time()

    print("")
    print("Completed in {0:.3f} seconds.".format(end-start))
    print("")

if __name__ == "__main__":
    main()
    
    