import os
import cv2
from tesseract_utils import read_boxfile, write_boxfile
from os import listdir
from os.path import isfile, join

IMAGE_EXTENSIONS= ['.png','.tif','.jpg', '.jpeg']
DATA_DIRECTORY= 'data/'
GROUND_EXTENSIONS= ['.box']
GROUND_EXTENSIONS_DEFAULT=GROUND_EXTENSIONS[0]

def split_extension( path ):
    '''splits filename (with extension) into filename and extension'''
    try:
        i=path.index(".", -5)
        return path[:i], path[i:]
    except ValueError:
        return path, ""

def try_extensions( path, extensions=IMAGE_EXTENSIONS ):
    '''checks if various extensions of a path exist'''
    if os.path.exists( path ):
        return path
    for ext in extensions:
        p= path+ext
        if os.path.exists( p ):
            return p
    return None

def get_image_filenames(path):
    onlyfiles = [ join(path,f) for f in listdir(path) if isfile(join(path,f)) and f.lower().endswith(tuple(IMAGE_EXTENSIONS)) ]
    return onlyfiles

def find_image_file(filename):
    ''' Return filename if file exists and has a valid image extension.
    Extension is optional. Also looks in the data directory if the given name doesn't work.
    '''
    good_path= try_extensions( filename, IMAGE_EXTENSIONS )
    if not good_path:
        good_path= try_extensions( os.path.join( DATA_DIRECTORY, filename ), IMAGE_EXTENSIONS )
    return good_path


class GroundFile( object ):
    def __init__(self, path):
        self.path=      path
        self.segments=  None
        self.classes=    None

    def read(self):
        self.classes, self.segments= read_boxfile( self.path )

    def write(self):
        write_boxfile( self.path, self.classes, self.segments )


class ImageFile( object ):
    '''An OCR image file. Has an image and its file path, and optionally 
    a ground (ground segments and classes) and it's file path'''
    def __init__( self, filename):
        good_path= find_image_file(filename)
        if not good_path:
            raise Exception( "could not find file: "+ filename)
        self.image_path = good_path
        self.image= cv2.imread(self.image_path)
        basename= split_extension(good_path)[0]
        self.ground_path=    try_extensions( basename, GROUND_EXTENSIONS )
        if self.ground_path:
            self.ground= GroundFile(self.ground_path)
            self.ground.read()
        else:
            self.ground_path= basename+GROUND_EXTENSIONS_DEFAULT
            self.ground=None

    def isGrounded(self):
        '''checks if this file is grounded'''
        return not (self.ground is None)

    def set_ground( self, segments, classes, write_file=False):
        '''creates the ground, saves it to a file'''
        if self.isGrounded():
            print "Warning: grounding already grounded file"
        self.ground= GroundFile(self.ground_path)
        self.ground.segments= segments
        self.ground.classes= classes
        if write_file:
            self.ground.write()

    def remove_ground(self, remove_file=False):
        '''removes ground, optionally deleting it's file'''
        if not self.isGrounded():
            print "Warning: ungrounding ungrounded file"
        self.ground= None
        if remove_file:
            os.remove( self.ground_path )
