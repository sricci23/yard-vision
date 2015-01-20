#!/usr/bin/env python

'''
This program can be used to experiment with adaptive thresholding.
Use the sliders to experiment with the C and Blocksize parameters.
When a key is pressed, the program exits, printing the final selections to console.

Usage:
    adaptivethreshold.py <filename>
Trackbars control the parameters to adaptiveThreshold
'''

import numpy as np
import cv2
import sliderparam as cvparam


def updateUseGaussian(n):
    cvparam_dict['useGaussian'].assignFromSlider(n)
    updateImage()

def updateInvert(n):
    cvparam_dict['invert'].assignFromSlider(n)
    updateImage()

def updateBlockSize(n):
    cvparam_dict['blockSize'].assignFromSlider(n)
    updateImage()

def updateC(n):
    cvparam_dict['c'].assignFromSlider(n)
    updateImage()

def mapBlockSizeSliderToValue(n):
    return n*2 + 3

def mapBlockSizeValueToSlider(n):
    return (n - 3)/2



def updateImage():
    c = cvparam_dict['c'].value
    blockSize = cvparam_dict['blockSize'].value
    threshMethod = cv2.ADAPTIVE_THRESH_GAUSSIAN_C if cvparam_dict['useGaussian'].value > 0 else cv2.ADAPTIVE_THRESH_MEAN_C
    threshType = cv2.THRESH_BINARY_INV if cvparam_dict['invert'].value > 0 else cv2.THRESH_BINARY

    image = cv2.adaptiveThreshold(img, maxValue=255, adaptiveMethod=threshMethod, thresholdType=threshType, blockSize=blockSize, C=c)
    cv2.imshow('results', image)


if __name__ == '__main__':
    print __doc__

    cvparam_dict = {}
    cvparam_dict['useGaussian'] = cvparam.sliderparam("Use Gaussian", 1, 1, updateUseGaussian)
    cvparam_dict['invert'] = cvparam.sliderparam("Invert", 1, 0, updateInvert)
    cvparam_dict['blockSize'] = cvparam.sliderparam("Block Size (3,5,..)", 21, 5, updateBlockSize, sliderToValue=mapBlockSizeSliderToValue, valueToSlider=mapBlockSizeValueToSlider)
    cvparam_dict['c'] = cvparam.sliderparam("C", 30, 5, updateC)

    import argparse
    parser = argparse.ArgumentParser(description="Interactively experiment with adaptiveThreshold parameters.")
    parser.add_argument('file', help='image to threshold', type=str)
    # add a command line parameter for every slider parameter
    cvparam.addCommandLineArgs(cvparam_dict, parser)

    args = parser.parse_args()
    cvparam.setValuesFromCommandLine(cvparam_dict, args)

    img = cv2.imread(args.file)
    assert img is not None, "File " + args.file + " was not found."
    img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    h, w = img.shape[:2]

    cv2.imshow('results', img) # window needs to exist before we add sliders
    cvparam.addSlidersToWindow(cvparam_dict, "results")
    updateImage()

    0xFF & cv2.waitKey()
    cv2.destroyAllWindows()

    # print selected parameters to console
    cvparam.dump(cvparam_dict)
