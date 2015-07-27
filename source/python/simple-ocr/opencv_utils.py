from numpy_utils import OverflowPreventer
from processor import DisplayingProcessor, ProcessorStack
import numpy
import cv2
import Image

class ImageProcessor( DisplayingProcessor ):
    def display( self, display_before=True ):
        key = 0
        if display_before:
            key = show_image_and_wait_for_key(self._input, "before "+self.__class__.__name__)
        if key != 27:
            key = show_image_and_wait_for_key(self._output,  "after " +self.__class__.__name__)
        return key
    def _process( self, image ):
        return self._image_processing( image )
    def _image_processing( self , image ):
        raise NotImplementedError( str(self.__class__) )

class BrightnessProcessor( ImageProcessor ):
    '''changes image brightness. 
    A brightness of -1 will make the image all black; 
    one of 1 will make the image all white'''
    PARAMETERS= ImageProcessor.PARAMETERS + {"brightness":0.0}
    def _image_processing( self , image ):
        b= self.brightness
        assert image.dtype==numpy.uint8
        assert -1<=b<=1
        image= image.copy()
        with OverflowPreventer(image) as img:
            img+=b*256
        return image

class ContrastProcessor( ImageProcessor ):
    '''changes image contrast. a scale of 1 will make no changes'''
    PARAMETERS= ImageProcessor.PARAMETERS + {"scale":1.0, "center":0.5}
    def _image_processing( self , image ):
        assert image.dtype==numpy.uint8
        image= image.copy()
        s,c= self.scale, self.center
        c= int(c*256)
        with OverflowPreventer(image) as img:
            if s<=1:
                img*=s
                img+= int(c*(1-s))
            else:
                img-=c*(1 - 1/s)
                img*=s
        return image

class BlurProcessor( ImageProcessor ):
    '''blurs image'''
    PARAMETERS= ImageProcessor.PARAMETERS + {"blur_x":3, "blur_y":3}
    def _image_processing( self , image ):
        assert image.dtype==numpy.uint8
        image= image.copy()
        x,y= self.blur_x, self.blur_y
        if x or y:
            x+= (x+1)%2 #opencv needs a
            y+= (y+1)%2 #odd number...
            image = cv2.GaussianBlur(image,(x,y),0)
        return image

def ask_for_key( return_arrow_keys=True ):
    key=128
    while key > 127:
        key=cv2.waitKey(0)
        if return_arrow_keys:
            if key in (65362,65364,65361,65363): #up, down, left, right
                return key
        key %= 256
    return key

def background_color( image, numpy_result=True ):
    ''' median calculation returns the predominant "color" (shade of grey) '''
    result= numpy.median(numpy.median(image, 0),0).astype( numpy.int )
    if not numpy_result:
        try:
            result= tuple(map(int, result))
        except TypeError:
            result= (int(result),)
    return result
    
def show_image_and_wait_for_key( image, label="Image", return_arrow_keys=False ):
    '''Shows an image, waits for a key, returns that key. Option to allow arrow keys '''
    print "showing",label,"(waiting for input)"
    cv2.namedWindow( 'norm', cv2.WINDOW_NORMAL);
    cv2.resizeWindow('norm', 1000, 1000 );
    cv2.imshow('norm',image)
    key = ask_for_key(return_arrow_keys)
    cv2.destroyWindow('norm')
    return key



def draw_segments( image , segments, color=(255,0,0), line_width=1):
    '''draws segments on image'''
    for segment in segments:
        x,y,w,h= segment
        cv2.rectangle(image,(x,y),(x+w,y+h),color,line_width)

def draw_lines( image, ys, color= (255,0,0), line_width=1):
    '''draws horizontal lines'''
    for y in ys:
        cv2.line( image, (0,y), (image.shape[1], y), color, line_width )


def draw_classes( image, segments, classes, color=(255,0,0), font_scale=1.0, line_width=1 ):
    assert len(segments)==len(classes)
    for s,uc in zip(segments, classes):
        x,y,w,h=s
        try:
            c=unichr(uc)
        except:
            c=uc
        cv2.putText(image, c, (x,y+h), cv2.FONT_HERSHEY_PLAIN, font_scale, color, line_width, bottomLeftOrigin=False)
        
def threshold(image):
    return cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 10)

def create_dummy_image(image_name, segment, dummy_name):
    image = cv2.imread(image_name, cv2.IMREAD_GRAYSCALE)
    cropped = image[segment[1] : segment[1] + segment[3], segment[0] : segment[0] + segment[2]]
    processed = threshold(cropped)
    cv2.imwrite(dummy_name, processed)