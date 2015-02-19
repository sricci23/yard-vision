from opencv_utils import show_image_and_wait_for_key, BrightnessProcessor, draw_segments, draw_lines
from segmentation_aux import contained_segments_matrix, LineFinder, guess_segments_lines
from processor import DisplayingProcessor, create_broadcast
import numpy
import math


def create_default_filter_stack():
    stack= [LargeFilter(), SmallFilter(), LargeAreaFilter(), ContainedFilter(), LineFinder(), NearLineFilter()]
    stack[4].add_poshook( create_broadcast( "lines_topmiddlebottoms", stack[5] ) )
    return stack

def create_min_filter_stack():
    stack= [RatioFilter(), LargeFilter(), SmallFilter(), NeighborFilter(), ThinPairFilter(), AlignmentFilter(), AlignmentFilter(), GroupFilter(), GroupFilter()]
    return stack


class Filter( DisplayingProcessor ):
    PARAMETERS= DisplayingProcessor.PARAMETERS
    '''A filter processes given segments, returning only the desirable
    ones'''
    def display( self, display_before=False):
        '''shows the effect of this filter'''
        try:
            copy= self.image.copy()
        except AttributeError:
            raise Exception("You need to set the Filter.image attribute for displaying")
        copy= BrightnessProcessor(brightness=0.6).process( copy )
        s, g= self._input, self.good_segments_indexes
        draw_segments( copy, s[g], (0,255,0) )
        draw_segments( copy, s[True-g], (0,0,255) )
        show_image_and_wait_for_key( copy, "segments filtered by "+self.__class__.__name__)
    def _good_segments( self, segments ):
        raise NotImplementedError
    def _process( self, segments):
        good= self._good_segments(segments)
        self.good_segments_indexes= good
        segments= segments[good]  
        return segments

class LargeFilter( Filter ):
    '''desirable segments are larger than some width or height'''
    PARAMETERS= Filter.PARAMETERS + {"min_width":10, "min_height":20}
    def _good_segments( self, segments ):
        good_width=  segments[:,2] >= self.min_width
        good_height= segments[:,3] >= self.min_height
        return good_width * good_height  #AND

class SmallFilter( Filter ):
    '''desirable segments are smaller than some width or height'''
    PARAMETERS= Filter.PARAMETERS + {"max_width":60, "max_height":100}
    def _good_segments( self, segments ):
        good_width=  segments[:,2]  <= self.max_width
        good_height= segments[:,3] <= self.max_height
        return good_width * good_height  #AND
        
class LargeAreaFilter( Filter ):
    '''desirable segments' area is larger than some'''
    PARAMETERS= Filter.PARAMETERS + {"min_area":45}
    def _good_segments( self, segments ):
        return (segments[:,2]*segments[:,3]) >= self.min_area

class ContainedFilter( Filter ):
    '''desirable segments are not contained by any other'''
    def _good_segments( self, segments ):
        m= contained_segments_matrix( segments )
        return (True - numpy.max(m, axis=1))

class NearLineFilter( Filter ):
    PARAMETERS= Filter.PARAMETERS + {"nearline_tolerance":5.0} # percentage distance stddev
    '''desirable segments have their y near a line'''
    def _good_segments( self, segments ):
        lines= guess_segments_lines(segments, self.lines_topmiddlebottoms, nearline_tolerance=self.nearline_tolerance)
        good= lines!=-1
        return good

class RatioFilter( Filter ):
    '''desirable segments have a height-to-width ratio within a certain range'''
    PARAMETERS= Filter.PARAMETERS + {"min_ratio":1.0, "max_ratio":2.0}
    def _good_segments( self, segments ):
        ratio= segments[:,3] / segments[:,2].astype(float)
        good=  ratio <= self.max_ratio
        good= good * (ratio >= self.min_ratio) #AND
        return good
    
class NeighborFilter(Filter):
    '''desirable segments are near other segments of equal height'''
    PARAMETERS = Filter.PARAMETERS + {"spacing_multiplier":0.3, "horizontal_multiplier":1, "min_height":0.8, "max_height":1.2}
    def _good_segments(self, segments):
        good = numpy.ndarray(shape=(len(segments)), dtype=bool)
        for i in range(0, len(good)):
            good[i] = False
        for i in range(0, len(segments)):
            if (good[i] == False):
                segment_1 = segments[i]
                for j in range(0, len(segments)):
                    if (i != j):
                        segment_2 = segments[j]
                        if (self.is_neighbor(segment_1, segment_2) and self.equal_height(segment_1, segment_2)):
                            good[i] = True
                            good[j] = True
                            break
        return good
    
    def is_neighbor(self, segment_1, segment_2):
        top_left_1_x = segment_1[0]
        top_left_1_y = segment_1[1]
        width_1 = segment_1[2]
        height_1 = segment_1[3]
        bottom_right_1_x = top_left_1_x + width_1
        bottom_right_1_y = top_left_1_y + height_1
        
        top_left_2_x = segment_2[0]
        top_left_2_y = segment_2[1]
        width_2 = segment_2[2]
        height_2 = segment_2[3]
        top_right_2_x = top_left_2_x + width_2
        top_right_2_y = top_left_2_y
        bottom_left_2_x = top_left_2_x
        bottom_left_2_y = top_left_2_y + height_2
        
        spacing_distance = height_1 * self.spacing_multiplier
        tl_to_bl_distance = self.manhattan_distance(top_left_1_x, top_left_1_y, bottom_left_2_x, bottom_left_2_y)
        tl_to_tr_distance = self.manhattan_distance(top_left_1_x, top_left_1_y, top_right_2_x, top_right_2_y)
        br_to_tr_distance = self.manhattan_distance(bottom_right_1_x, bottom_right_1_y, top_right_2_x, top_right_2_y)
        br_to_bl_distance = self.manhattan_distance(bottom_right_1_x, bottom_right_1_y, bottom_left_2_x, bottom_left_2_y)
        shortest_distance = min(tl_to_bl_distance, tl_to_tr_distance, br_to_tr_distance, br_to_bl_distance)
        return shortest_distance < spacing_distance
        
    def manhattan_distance(self, x_1, y_1, x_2, y_2):
        return self.horizontal_multiplier * math.fabs(int(x_1) - int(x_2)) + math.fabs(int(y_1) - int(y_2))
    
    def equal_height(self, segment_1, segment_2):
        height_1 = segment_1[3]
        height_2 = segment_2[3]
        height_ratio = float(height_1) / float(height_2)
        return height_ratio > self.min_height and height_ratio < self.max_height
    
class GroupFilter(NeighborFilter):
    '''desirable segments are in groups'''
    PARAMETERS = NeighborFilter.PARAMETERS + {"min_group_size":9, "min_aligned":2}
    def _good_segments(self, segments):
        self.spacing_multiplier = self.min_group_size + 2
        self.horizontal_multiplier = 1.25
        good = numpy.ndarray(shape=(len(segments)), dtype=bool)
        for i in range(0, len(good)):
            good[i] = False
        for i in range(0, len(segments)):
            segment_1 = segments[i]
            neighbors = 0
            aligned = 0
            for j in range(0, len(segments)):
                if (i != j):
                    segment_2 = segments[j]
                    if (self.is_neighbor(segment_1, segment_2)):
                        neighbors = neighbors + 1
                        x_distance = math.fabs(int(segment_1[0]) - int(segment_2[0]))
                        y_distance = math.fabs(int(segment_1[1]) - int(segment_2[1]))
            if (neighbors >= self.min_group_size):
                good[i] = True
        return good
        
class AlignmentFilter(NeighborFilter):
    '''desirable segments are aligned vertically or horizontally'''
    PARAMETERS = NeighborFilter.PARAMETERS + {"min_aligned":2, "alignment_factor":0.4}
    def _good_segments(self, segments):
        self.spacing_multiplier = self.min_aligned + 2
        good = numpy.ndarray(shape=(len(segments)), dtype=bool)
        for i in range(0, len(good)):
            good[i] = False
        for i in range(0, len(segments)):
            segment_1 = segments[i]
            aligned = 0
            for j in range(0, len(segments)):
                if (i != j):
                    segment_2 = segments[j]
                    if (self.is_neighbor(segment_1, segment_2)):
                        x_distance = math.fabs(int(segment_1[0]) - int(segment_2[0]))
                        y_distance = math.fabs(int(segment_1[1]) - int(segment_2[1]))
                        if (min(x_distance, y_distance) < segment_1[3] * self.alignment_factor):
                            aligned = aligned + 1
            if (aligned >= self.min_aligned):
                good[i] = True
        return good
    
class ThinPairFilter(NeighborFilter):
    '''neighboring segments with high height/width ratios are not desirable'''
    PARAMETERS = NeighborFilter.PARAMETERS + {"max_height_width_ratio":3}
    def _good_segments(self, segments):
        good = numpy.ndarray(shape=(len(segments)), dtype=bool)
        for i in range(0, len(good)):
            good[i] = True
        for i in range(0, len(segments)):
            segment_1 = segments[i]
            neighbors = 0
            aligned = 0
            for j in range(0, len(segments)):
                if (i != j):
                    segment_2 = segments[j]
                    if (self.is_neighbor(segment_1, segment_2)):
                        ratio_1 = float(segment_1[3]) / float(segment_1[2])
                        ratio_2 = float(segment_2[3]) / float(segment_2[2])
                        if (ratio_1 > self.max_height_width_ratio and ratio_2 > self.max_height_width_ratio):
                            good[i] = False
                            break
        return good