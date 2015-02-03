__author__ = 'mdiamond'

#!/usr/bin/env python

'''
Loads several images sequentially and tries to find contours in each image.

Press a key to switch images, <Esc> to end.
'''

import cv2
import sliderparam as cvparams


def find_contours(img):
    img = cv2.bilateralFilter(img, d=cvparam_dict['filterSize'].value,  sigmaColor=cvparam_dict['colorKernelSize'].value, sigmaSpace=cvparam_dict['spaceKernelSize'].value)
    bin = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    bin = cv2.adaptiveThreshold(bin, maxValue=255, adaptiveMethod=cv2.ADAPTIVE_THRESH_MEAN_C, thresholdType=cv2.THRESH_BINARY, blockSize=cvparam_dict['threshK'].value, C=cvparam_dict['threshC'].value)

    for i in xrange(cvparam_dict['erode'].value):
        bin = cv2.erode(bin, None)
    for i in xrange(cvparam_dict['dilate'].value):
        bin = cv2.dilate(bin, None)

    contours, hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    # for cnt in contours:
    #    cnt_len = cv2.arcLength(cnt, True)
    #    cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)
    #    squares.append(cnt)
    return contours



def updateImage():
    copy = img.copy()
    squares = find_contours(copy)
    cv2.drawContours(copy, squares, -1, (0, 255, 0), 1 )

    cvparams.annotateImageWithParams(cvparam_dict, copy)

    cv2.imshow('results', copy)

if __name__ == '__main__':
    print __doc__

    cvparam_dict = {}
    cvparam_dict['filterSize'] = cvparams.kernelparam("Filter Size", 100, 11, updateImage)
    cvparam_dict['spaceKernelSize'] = cvparams.kernelparam("Space Kernel Size", 150, 109, updateImage)
    cvparam_dict['colorKernelSize'] = cvparams.kernelparam("Color Kernel Size", 150, 109, updateImage)
    cvparam_dict['erode'] = cvparams.sliderparam("Erode", 2, 0, updateImage)
    cvparam_dict['dilate'] = cvparams.sliderparam("Dilate", 2, 0, updateImage)
    cvparam_dict['threshK'] = cvparams.kernelparam("ThreshK", 21, 11, updateImage)
    cvparam_dict['threshC'] = cvparams.sliderparam("ThreshC", 20, 10, updateImage)

    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', help='image(s) to process', type=str)
    # add a command line parameter for every slider parameter
    cvparams.addCommandLineArgs(cvparam_dict, parser)

    args = parser.parse_args()
    cvparams.setValuesFromCommandLine(cvparam_dict, args)

    from glob import glob
    for filename in glob(args.file):
        img = cv2.imread(filename)

        cv2.imshow('results', img) # window needs to exist before we add sliders
        cvparams.addSlidersToWindow(cvparam_dict, "results")
        updateImage()

        ch = cv2.waitKey()
        if ch == 27:
            break

    cv2.destroyAllWindows()
    cvparams.dump(cvparam_dict)
