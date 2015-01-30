#!/usr/bin/env python

'''
This program can be used to experiment with morphology gradient.
When a key is pressed, the next image (if any) is loaded. Esc key ends the program.
The final parameter values are printed to console.
'''

import numpy as np
import cv2
import sliderparam as cvparam


def updateImage():
    iter = cvparam_dict['iterations'].value
    size = cvparam_dict['size'].value
    if cvparam_dict['shape'].value == 0:
        shape = cv2.MORPH_ELLIPSE
    elif cvparam_dict['shape'].value == 1:
        shape = cv2.MORPH_RECT
    else:
        shape = cv2.MORPH_CROSS
    st = cv2.getStructuringElement(shape, (size, size))
    image = cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel=st, iterations=iter)
    cv2.imshow('results', image)


if __name__ == '__main__':
    print __doc__

    cvparam_dict = {}
    cvparam_dict['iterations'] = cvparam.sliderparam("Iterations", 5, 1, updateImage)
    cvparam_dict['shape'] = cvparam.sliderparam("K Ellipse/Rect/Cross", 2, 1, updateImage)
    cvparam_dict['size'] = cvparam.kernelparam("K Size", 21, 5, updateImage)

    import argparse
    parser = argparse.ArgumentParser(description="Interactively experiment with morphology gradient parameters.")
    parser.add_argument('file', help='image to threshold', type=str)
    # add a command line parameter for every slider parameter
    cvparam.addCommandLineArgs(cvparam_dict, parser)

    args = parser.parse_args()
    cvparam.setValuesFromCommandLine(cvparam_dict, args)

    from glob import glob
    for filename in glob(args.file):
        img = cv2.imread(filename)
        assert img is not None, "File " + args.file + " was not found."
        # img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        h, w = img.shape[:2]

        cv2.imshow('results', img) # window needs to exist before we add sliders
        cvparam.addSlidersToWindow(cvparam_dict, "results")
        updateImage()
        ch = cv2.waitKey()
        if ch == 27:
            break

    cv2.destroyAllWindows()

    # print selected parameters to console
    cvparam.dump(cvparam_dict)
