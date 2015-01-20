#!/usr/bin/env python

'''
This program can be used to experiment with Hough line detection.
Use the sliders to experiment with the parameters.
When a key is pressed, the program exits, printing the final selections to console.

Usage:
    hough_lines.py <filename>
'''

import numpy as np
import cv2
import sliderparam as cvparams

def get_image(fname):
    img = cv2.imread(fname)
    assert img is not None, "File " + fname + " was not found."
    return img

def updateThreshold(n):
    cvparam_dict['threshold'].value = n
    updateImage()

def updateMinLength(n):
    cvparam_dict['minLength'].value = n
    updateImage()

def updateMaxMergeGap(n):
    cvparam_dict['maxGapLength'].value = n
    updateImage()

def updateImage():
    theta = np.pi/180
    rho = 1
    threshold = cvparam_dict['threshold'].value
    minLength =  cvparam_dict['minLength'].value
    maxGapLength = cvparam_dict['maxGapLength'].value
    lines = cv2.HoughLinesP(edges, rho, theta, threshold=threshold, minLineLength=minLength, maxLineGap=maxGapLength)

    imag = img.copy()
    for x1,y1,x2,y2 in lines[0]:
        cv2.line(imag,(x1,y1),(x2,y2),(0,255,0),2)
    cvparams.annotateImageWithParams(cvparam_dict, imag)
    cv2.imshow('results', imag)

if __name__ == '__main__':
    print __doc__

    cvparam_dict = {}
    cvparam_dict['threshold'] = cvparams.sliderparam("Threshold", 500, 50, updateThreshold)
    cvparam_dict['minLength'] = cvparams.sliderparam("Min Length", 500, 100, updateMinLength)
    cvparam_dict['maxGapLength'] = cvparams.sliderparam("Max Gap", 500, 20, updateMaxMergeGap)

    import argparse
    parser = argparse.ArgumentParser(description="Interactively experiment with HoughLinesP parameters.")
    parser.add_argument('file', help='image to threshold', type=str)
    # add a command line parameter for every slider parameter
    cvparams.addCommandLineArgs(cvparam_dict, parser)

    args = parser.parse_args()
    cvparams.setValuesFromCommandLine(cvparam_dict, args)

    img = get_image(args.file)
    h, w = img.shape[:2]
    img = cv2.GaussianBlur(img, (5, 5), 0)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 600, 600, apertureSize=5)


    cv2.imshow('results', img) # window needs to exist before we add sliders
    cvparams.addSlidersToWindow(cvparam_dict, "results")
    updateImage()

    0xFF & cv2.waitKey()
    cv2.destroyAllWindows()

    cvparams.dump(cvparam_dict)
