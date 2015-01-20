__author__ = 'mdiamond'

import cv2
import argparse

class sliderparam():
    def __init__(self, description, maxValue, value, updateFn, sliderToValue=lambda(x):x, valueToSlider=lambda(x):x):
        assert value <= maxValue
        self.description = description
        self.maxValue = maxValue
        self.updateFn = updateFn
        self.mapSliderToValue = sliderToValue
        self.mapValueToSlider = valueToSlider
        self.value = value
        self.sliderValue = valueToSlider(value)
        self.maxSliderValue = valueToSlider(maxValue)

    def assignFromSlider(self, sliderValue):
        self.sliderValue = sliderValue
        self.value = self.mapSliderToValue(sliderValue)

    def assignFromValue(self, value):
        self.value = value
        self.sliderValue = self.mapValueToSlider(value)

    def createSlider(self, window):
        cv2.createTrackbar(self.description, window, self.sliderValue, self.maxSliderValue, self.updateFn)

    def __str__(self):
        return self.description + " = " + str(self.value)

def annotateImageWithParams(param_dict, image):
    y = 50
    for p in param_dict.itervalues():
        cv2.putText(image, text=str(p), org=(50, y), color=(0,255,0), fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=1.0)
        y += 30

def dump(param_dict):
    for k in param_dict.keys():
        p = param_dict[k]
        print "--" + k + "=" + str(p.value)

def addSlidersToWindow(param_dict, windowname):
    for p in param_dict.itervalues():
        p.createSlider(windowname)

def addCommandLineArgs(param_dict, parser):
    ''' define a command line parameter for every slider parameter
    :param dict: dictionary of sliderparam
    :param parser: argparse
    '''
    for k in param_dict.keys():
        argkey = '--' + k
        param = param_dict[k]
        parser.add_argument(argkey, help=param.description, type=int, default=param.value)

def setValuesFromCommandLine(param_dict, args):
    ''' read command line parameter for each slider parameter
    This allows any default value to be overridden by the command line.
    :param dict: dictionary of sliderparam
    :param args: parsed command line
    '''
    for k in param_dict.keys():
        p = param_dict[k]
        val = getattr(args, k)
        p.assignFromValue(val)


