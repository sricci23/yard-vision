#!/usr/bin/env python

'''
This program can be used to experiment with Canny edge detection.
Use the sliders to experiment with the parameters.
When a key is pressed, the program exits, printing the final selections to console.

Usage:
    canny.py <filename>
'''

import numpy as np
import cv2
import sliderparam as cvparams

def updateThreshold1(n):
    cvparam_dict['threshold1'].assignFromSlider(n)
    updateImage()

def updateThreshold2(n):
    cvparam_dict['threshold2'].assignFromSlider(n)
    updateImage()

def updateAperture(n):
    cvparam_dict['aperture'].assignFromSlider(n)
    updateImage()

def mapApertureSliderToValue(n):
    return n*2 + 3

def mapApertureValueToSlider(n):
    return (n - 3)/2

def updateImage():
    edges = cv2.Canny(gray, cvparam_dict['threshold1'].value, cvparam_dict['threshold2'].value, apertureSize=cvparam_dict['aperture'].value)

    imag = img.copy()
    imag /= 2
    imag[edges != 0] = (0, 255, 0)

    cvparams.annotateImageWithParams(cvparam_dict, imag)
    cv2.imshow('results', imag)


if __name__ == '__main__':
    print __doc__

    cvparam_dict = {}
    cvparam_dict['threshold1'] = cvparams.sliderparam("Threshold1", 6000, 2000, updateThreshold1)
    cvparam_dict['threshold2'] = cvparams.sliderparam("Threshold2", 6000, 4000, updateThreshold2)
    cvparam_dict['aperture'] = cvparams.sliderparam("Aperture (3, 5, 7)", 7, 5, updateAperture, mapApertureSliderToValue, mapApertureValueToSlider)


    import argparse
    parser = argparse.ArgumentParser(description="Interactively experiment with Canny operator.")
    parser.add_argument('file', help='image to threshold', type=str)
    parser.add_argument('--blur', help='Gaussian blur option', action='store_true')
    # add a command line parameter for every slider parameter
    cvparams.addCommandLineArgs(cvparam_dict, parser)

    args = parser.parse_args()
    cvparams.setValuesFromCommandLine(cvparam_dict, args)

    img = cv2.imread(args.file)
    assert img is not None, "File " + args.file + " was not found."
    h, w = img.shape[:2]
    if args.blur:
        img = cv2.GaussianBlur(img, (5, 5), 0)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    cv2.imshow('results', img) # window needs to exist before we add sliders
    cvparams.addSlidersToWindow(cvparam_dict, "results")
    updateImage()

    0xFF & cv2.waitKey()
    cv2.destroyAllWindows()

    print "Gaussian blur = " + ("True" if args.blur else "False")
    print
    cvparams.dump(cvparam_dict)
