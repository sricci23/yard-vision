#!/usr/bin/env python

'''
This program can be used to experiment with Sobel edge detection.
Use the sliders to experiment with the parameters.
When a key is pressed, the next image (if any) is loaded. Esc key ends the program.
The final parameter values are printed to console.
'''

import numpy as np
import cv2
import sliderparam as cvparams

def updateImage():
    destDepth = cv2.CV_32F; # should be higher than source depth to avoid overflow
    imgCopy = cv2.Sobel(img, ddepth=destDepth, dx=cvparam_dict['dx'].value, dy=cvparam_dict['dy'].value, ksize=cvparam_dict['kernelSize'].value,
                      scale=cvparam_dict['scale'].value, delta=cvparam_dict['delta'].value)

    cvparams.annotateImageWithParams(cvparam_dict, imgCopy)
    cv2.imshow('results', imgCopy)


if __name__ == '__main__':
    print __doc__

    cvparam_dict = {}
    cvparam_dict['dx'] = cvparams.sliderparam("dx", 2, 1, updateImage)
    cvparam_dict['dy'] = cvparams.sliderparam("dy", 2, 1, updateImage)
    cvparam_dict['kernelSize'] = cvparams.kernelparam("Kernel (3, 5,..)", 21, 5, updateImage)
    cvparam_dict['delta'] = cvparams.sliderparam("delta", 5, 0, updateImage)
    cvparam_dict['scale'] = cvparams.sliderparam("scale", 2, 1, updateImage)

    import argparse
    parser = argparse.ArgumentParser(description="Apply Sobel operator.")
    parser.add_argument('file', help='image to process', type=str)
    # add a command line parameter for every slider parameter
    cvparams.addCommandLineArgs(cvparam_dict, parser)

    args = parser.parse_args()
    cvparams.setValuesFromCommandLine(cvparam_dict, args)

    from glob import glob
    for filename in glob(args.file):
        img = cv2.imread(filename)
        assert img is not None, "File " + args.file + " was not found."
        h, w = img.shape[:2]
        imgCopy = cv2.bilateralFilter(img, d=11, sigmaColor=109, sigmaSpace=109)

        cv2.imshow('results', img) # window needs to exist before we add sliders
        cvparams.addSlidersToWindow(cvparam_dict, "results")
        updateImage()

        ch = cv2.waitKey()
        if ch == 27:
            break

    cv2.destroyAllWindows()

    cvparams.dump(cvparam_dict)
