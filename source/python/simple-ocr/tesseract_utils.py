import numpy

from classification import classes_from_numpy, classes_to_numpy
from segmentation import segments_from_numpy, segments_to_numpy
from operator import itemgetter


    
def read_boxfile( path ):
    classes=  []
    segments= []
    with open(path) as f:
        for line in f:
            s= line.split(" ")
            assert len(s)==6
            assert s[5]=='0\n'
            classes.append( s[0].decode('utf-8') )
            segments.append( map(int, s[1:5]))
    return classes_to_numpy(classes), segments_to_numpy(segments)

def write_boxfile(path, classes, segments):
    classes, segments= classes_from_numpy(classes), segments_from_numpy(segments)
    with open(path, 'w') as f:
        for c,s in zip(classes, segments):
            f.write( c.encode('utf-8')+' '+ ' '.join(map(str, s))+" 0\n")
            
def get_whitelist(target_segment, segments, pattern):
    numbers = "0123456789"
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    last_letters = "UZ"
    if (pattern is None):
        return numbers + letters
    if (pattern == "H1"):
        horizontal_order = sorted(segments, key=itemgetter(0))
        for i in range(0, 4):
            current_segment = horizontal_order[i]
            if (numpy.all(target_segment == current_segment)):
                if i == 3:
                    return last_letters
                return letters
    elif (pattern == "H2"):
        vertical_order = sorted(segments, key=itemgetter(1))
        horizontal_order = sorted(vertical_order[:4], key=itemgetter(0))
        for i in range(0, 4):
            current_segment = horizontal_order[i]
            if (numpy.all(target_segment == current_segment)):
                if i == 3:
                    return last_letters
                return letters
    elif (pattern == "V1"):
        vertical_order = sorted(segments, key=itemgetter(1))
        for i in range(0, 4):
            current_segment = vertical_order[i]
            if (numpy.all(target_segment == current_segment)):
                if i == 3:
                    return last_letters
                return letters
    elif (pattern == "V2"):
        horizontal_order = sorted(segments, key=itemgetter(0))
        vertical_order = sorted(horizontal_order[:4], key=itemgetter(1))
        for i in range(0, 4):
            current_segment = vertical_order[i]
            if (numpy.all(target_segment == current_segment)):
                if i == 3:
                    return last_letters
                return letters
    return numbers

def get_pattern(cluster_segments):
    if (len(cluster_segments) != 10):
        return None
    expected_group_distance_factor = 7
    horizontal_order = sorted(cluster_segments, key=itemgetter(0))
    vertical_order = sorted(cluster_segments, key=itemgetter(1))
    max_horizontal_distance = horizontal_order[9][0] - horizontal_order[0][0]
    max_vertical_distance = vertical_order[9][1] - vertical_order[0][1]
    if (max_horizontal_distance > max_vertical_distance):
        if (max_horizontal_distance < horizontal_order[0][2] * expected_group_distance_factor):
            return "H2"
        return "H1"
    if (max_vertical_distance < vertical_order[0][3] * expected_group_distance_factor):
        return "V2"
    return "V1"
    
def is_cluster_match(cluster_1, cluster_2):
    cluster_match = True
    for i in range(0, len(cluster_1)):
        segment_1 = cluster_1[i]
        segment_2 = cluster_2[i]
        for j in range(0, len(segment_1)):
            value_1 = segment_1[j]
            value_2 = segment_2[j]
            cluster_match = cluster_match and value_1 == value_2
            if cluster_match == False:
                return cluster_match
    return cluster_match