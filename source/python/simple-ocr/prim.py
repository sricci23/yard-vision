import numpy
import math
from numpy.core.multiarray import ndarray
from operator import itemgetter
import copy

def get_cluster(target_segment, segments):
    max_cluster_distance_factor = 3
    cluster_segments = [target_segment]
    non_cluster_segments = numpy.ndarray(shape = (len(segments), 5))
    for i in range(0, len(non_cluster_segments)):
        segment = segments[i]
        segment = numpy.append(segment, 0)   
        non_cluster_segments[i] = segment
    index = -1
    for i in range(0, len(non_cluster_segments)):
        current_segment = non_cluster_segments[i]
        if (numpy.all(target_segment == current_segment[:4])):
            index = i
            break
    non_cluster_segments = numpy.delete(non_cluster_segments, index, 0)
    while len(cluster_segments) < 10 and len(non_cluster_segments) > 0:
        non_cluster_segments = recalculate_distances(cluster_segments, non_cluster_segments)
        new_cluster_segment = non_cluster_segments[0]
        if (len(cluster_segments) > 1 and new_cluster_segment[4] > get_average_nearest_neighbor_distance(cluster_segments) * max_cluster_distance_factor):
            break
        cluster_segments.append(new_cluster_segment[:4])
        non_cluster_segments.remove(new_cluster_segment)
    return cluster_segments
    
def get_distance(segment_1, segment_2):
    return math.sqrt(math.pow(int(segment_1[0]) - int(segment_2[0]), 2) + math.pow(int(segment_1[1]) - int(segment_2[1]), 2))

def recalculate_distances(cluster_segments, non_cluster_segments):
    for current_segment in non_cluster_segments:
        distance = -1
        for cluster_segment in cluster_segments:
            new_distance = get_distance(current_segment, cluster_segment)
            if (distance < 0 or new_distance < distance):
                distance = new_distance
        current_segment[4] = distance
    non_cluster_segments = sorted(non_cluster_segments, key=itemgetter(4))
    return non_cluster_segments

def get_average_nearest_neighbor_distance(cluster_segments):
    total_distance = 0.0
    for segment_1 in cluster_segments:
        segment_distance = -1.0
        for segment_2 in cluster_segments:
            if (numpy.all(segment_1 == segment_2) == False):
                new_distance = get_distance(segment_1, segment_2)
                if (segment_distance < 0 or new_distance < segment_distance):
                    segment_distance = new_distance
        total_distance = total_distance + segment_distance
    return total_distance / len(cluster_segments)