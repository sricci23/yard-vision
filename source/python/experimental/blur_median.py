#!/usr/bin/env python

'''
This program can be used to experiment with Median blur.
Use the sliders to experiment with the parameters.
When a key is pressed, the next image (if any) is loaded. Esc key ends the program.
The final parameter values are printed to console.
'''

import numpy as np
import cv2
import sliderparam as cvparams

def updateImage():
    w = cvparam_dict['kernelSize'].value
    imgCopy = cv2.medianBlur(img, w)

    cvparams.annotateImageWithParams(cvparam_dict, imgCopy)
    cv2.imshow('results', imgCopy)

if __name__ == '__main__':
    print __doc__

    cvparam_dict = {}
    cvparam_dict['kernelSize'] = cvparams.kernelparam("Kernel X (3,5..)", 51, 5, updateImage)

    import argparse
    parser = argparse.ArgumentParser(description="Apply median blur operator.")
    parser.add_argument('file', help='image to threshold', type=str)
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
