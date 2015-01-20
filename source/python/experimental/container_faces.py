__author__ = 'mdiamond'

#!/usr/bin/env python

'''
Loads several images sequentially and tries to find container faces in each image.

Press a key to switch images, <Esc> to end.
'''

import numpy as np
import math
import cv2
import sliderparam as cvparam

def angle_cos(p0, p1, p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )

def find_containers_by_contour(img):
    img = cv2.GaussianBlur(img, (5, 5), 0)

    squares = []
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # try various thresholds
    for thrs in xrange(0, 255, 26):
        if thrs == 0:
            bin = cv2.Canny(gray, 0, 50, apertureSize=5)
            bin = cv2.dilate(bin, None)
        else:
            retval, bin = cv2.threshold(gray, thrs, 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            cnt_len = cv2.arcLength(cnt, True)
            cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)
            # if convex quadrilateral & large enough
            if len(cnt) == 4 and cv2.contourArea(cnt) > 4000 and cv2.isContourConvex(cnt):
                squares.append(cnt)
    return squares

def find_lines(img):
    img = cv2.GaussianBlur(img, (5, 5), 0)

    # canny operator
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 600, 600, apertureSize=5)

    # hough_lines
    minLength = 350
    maxMergeGap = 45
    threshold = 140
    theta = np.pi/180
    rho = 1
    lines = cv2.HoughLinesP(edges, rho, theta, threshold=threshold, minLineLength=minLength, maxLineGap=maxMergeGap)
    return lines[0]

def find_vertical_lines(lines):
    vert_lines = []
    for line in lines:
        x1,y1,x2,y2 = line
        rad = math.atan2(y2-y1, x2-x1)
        angle = abs(math.degrees(rad))
        if abs(angle - 90) < cvparam_dict['maxDegFromVert'].value:
            vert_lines.append(line)
    return vert_lines


def updateMaxVertAngle(n):
    global vert_lines
    cvparam_dict['maxDegFromVert'].assignFromSlider(n)
    vert_lines = find_vertical_lines(lines)
    updateImage()

def draw_lines(img, lines, color=(0,255,0)):
    for x1,y1,x2,y2 in lines:
        cv2.line(img,(x1,y1),(x2,y2),color,2)


def updateImage():
    copy = img.copy()
    draw_lines(copy, lines)
    draw_lines(copy, vert_lines, color=(255,127,0))
    cv2.imshow('results', copy)

if __name__ == '__main__':
    print __doc__

    cvparam_dict = {}
    cvparam_dict['maxDegFromVert'] = cvparam.sliderparam("Deg From Vert", 90, 10, updateMaxVertAngle)

    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', help='image(s) to threshold', type=str)
    # add a command line parameter for every slider parameter
    cvparam.addCommandLineArgs(cvparam_dict, parser)

    args = parser.parse_args()
    cvparam.setValuesFromCommandLine(cvparam_dict, args)

    from glob import glob
    for filename in glob(args.file):
        img = cv2.imread(filename)

        # extract lines
        lines = find_lines(img)
        # find verticals
        vert_lines = find_vertical_lines(lines)

        cv2.imshow('results', img) # window needs to exist before we add sliders
        cvparam.addSlidersToWindow(cvparam_dict, "results")
        updateImage()

        ch = cv2.waitKey()
        if ch == 27:
            cv2.destroyAllWindows()
            exit()
