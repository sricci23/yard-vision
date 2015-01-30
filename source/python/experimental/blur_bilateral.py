#!/usr/bin/env python

'''
This program can be used to experiment with Bilateral filtering (blur).
Use the sliders to experiment with the parameters.
When a key is pressed, the next image (if any) is loaded. Esc key ends the program.
The final parameter values are printed to console.
'''

import numpy as np
import cv2
import sliderparam as cvparams

def updateImage():
    d = cvparam_dict['filterSize'].value
    sigmaColor = cvparam_dict['colorKernelSize'].value
    sigmaSpace = cvparam_dict['spaceKernelSize'].value
    imgCopy = cv2.bilateralFilter(img, d=d, sigmaColor=sigmaColor, sigmaSpace=sigmaSpace)

    cvparams.annotateImageWithParams(cvparam_dict, imgCopy)
    cv2.imshow('results', imgCopy)

if __name__ == '__main__':
    print __doc__

    cvparam_dict = {}
    cvparam_dict['filterSize'] = cvparams.kernelparam("Filter Size", 100, 11, updateImage)
    cvparam_dict['spaceKernelSize'] = cvparams.kernelparam("Space Kernel Size", 150, 109, updateImage)
    cvparam_dict['colorKernelSize'] = cvparams.kernelparam("Color Kernel Size", 150, 109, updateImage)

    import argparse
    parser = argparse.ArgumentParser(description="Apply bilateral (edge preserving) blur operator.")
    parser.add_argument('file', help='image to blur (wildcards ok)', type=str)
    # add a command line parameter for every slider parameter
    cvparams.addCommandLineArgs(cvparam_dict, parser)

    args = parser.parse_args()
    cvparams.setValuesFromCommandLine(cvparam_dict, args)

    from glob import glob
    for filename in glob(args.file):
        img = cv2.imread(filename)
        assert img is not None, "File " + args.file + " was not found."
        h, w = img.shape[:2]

        cv2.imshow('results', img) # window needs to exist before we add sliders
        cvparams.addSlidersToWindow(cvparam_dict, "results")
        updateImage()

        ch = cv2.waitKey()
        if ch == 27:
            break

    cv2.destroyAllWindows()

    cvparams.dump(cvparam_dict)
