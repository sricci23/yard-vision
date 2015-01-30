#!/usr/bin/env python

'''
This program can be used to experiment with Canny edge detection.
Use the sliders to experiment with the parameters.
When a key is pressed, the next image (if any) is loaded. Esc key ends the program.
The final parameter values are printed to console.
'''

import numpy as np
import cv2
import sliderparam as cvparams

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
    cvparam_dict['threshold1'] = cvparams.sliderparam("Threshold1", 2000, 500, updateImage)
    cvparam_dict['threshold2'] = cvparams.sliderparam("Threshold2", 2000, 2000, updateImage)
    cvparam_dict['aperture'] = cvparams.kernelparam("Aperture (3, 5, 7)", 7, 5, updateImage)


    import argparse
    parser = argparse.ArgumentParser(description="Interactively experiment with Canny operator.")
    parser.add_argument('file', help='image to threshold (wildcard ok)', type=str)
    parser.add_argument('--blur', help='blur preprocessing', action='store_true')
    # add a command line parameter for every slider parameter
    cvparams.addCommandLineArgs(cvparam_dict, parser)

    args = parser.parse_args()
    cvparams.setValuesFromCommandLine(cvparam_dict, args)

    from glob import glob
    for filename in glob(args.file):
        img = cv2.imread(filename)
        assert img is not None, "File " + args.file + " was not found."
        h, w = img.shape[:2]
        if args.blur:
            img = cv2.GaussianBlur(img, (5, 5), 0)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        cv2.imshow('results', img) # window needs to exist before we add sliders
        cvparams.addSlidersToWindow(cvparam_dict, "results")
        updateImage()

        ch = cv2.waitKey()
        if ch == 27:
            break

    cv2.destroyAllWindows()
    print "blur = " + ("True" if args.blur else "False")
    print
    cvparams.dump(cvparam_dict)
