#!/usr/bin/env python
# coding: utf-8

import os
import sys
import xml.etree.ElementTree as ET
from multiprocessing import Pool

verbose = True

labels = {}
with open("../labels.txt") as label_file:
    for line_num, label in enumerate(label_file):
        if label[-1] == "\n":
            label = label[0:-1:1]
        labels[label] = line_num

def get_img_dims(root):
    dims = {'width' : None,
            'height' : None,
            'depth' : None
           }   
    for dim in dims:
        dims[dim] = float(root.findall("./size/{}".format(dim))[0].text)
    return dims

def get_bboxes(root, labels):
    bboxes = []
    dims = get_img_dims(root)
    
    for object in root.findall("./object"):
        box = {'label_idx' : None,
               'x_mid' : None, 
               'y_mid' : None,
               'width' : None,
               'height' : None
              }
        
        label = object.find('name').text
        box['label_idx'] = labels[label]
        
        xmin = float(object.find('bndbox').find('xmin').text)
        ymin = float(object.find('bndbox').find('ymin').text)
        xmax = float(object.find('bndbox').find('xmax').text)
        ymax = float(object.find('bndbox').find('ymax').text)
        
        box['x_mid'] = (xmax + xmin)/(2 * dims['width'])
        box['y_mid'] = (ymax + ymin)/(2 * dims['height'])
        box['width'] = (xmax - xmin)/(dims['width'])
        box['height'] = (ymax - ymin)/(dims['height'])
        
        bboxes.append(box)
    return bboxes

def generate_text_file(bboxes):
    lines = []
    for box in bboxes:
        lines.append("{} {} {} {} {}".format(box['label_idx'],
                                             box['x_mid'],
                                             box['y_mid'], 
                                             box['width'], 
                                             box['height']
                                            )
                    )
    return '\n'.join(lines)

def convert_file(filepath):
    root = ET.parse(filepath)
    filename = filepath.split('/')[-1]
    file = {'filepath' : filepath,
            'contents' : generate_text_file(get_bboxes(root, labels))
           }
    return file

def write_converted_file(filepath):
    converted = convert_file(filepath)
    filename = converted['filepath'].split('/')[-1]
    new_filename = '.'.join(filename.split(".")[:-1:] + ['txt'])
    fileroot = '/'.join(converted['filepath'].split('/')[:-1:])
    newfullpath = fileroot + '/txt/' + new_filename
    try:
        with open(newfullpath, 'w') as txt_file:
            txt_file.write(converted['contents'])
    except FileNotFoundError:
        os.mkdir(fileroot + '/txt')
        with open(fileroot + '/txt/' + new_filename, 'w') as txt_file:
            txt_file.write(converted['contents'])
    if verbose == True:
        print("Wrote file to: {}".format(newfullpath))

class FileGenerator(object): #Lazy execution
    def __init__(self, subdir, ext = 'xml'):
        self.subdir = subdir
        self.ext = ext
        self.gen = os.scandir(subdir)

    def __call__(self):
        for entry in self.gen:
            if not entry.name.startswith('.') and entry.is_file() and entry.name.split(".")[-1].lower() == self.ext:
                yield "{}/{}".format(self.subdir, entry.name)


def getThreads():
    """ Returns the number of available threads on a posix/win based system """
    if sys.platform == 'win32':
        return (int)(os.environ['NUMBER_OF_PROCESSORS'])
    else:
        return (int)(os.popen('grep -c cores /proc/cpuinfo').read())