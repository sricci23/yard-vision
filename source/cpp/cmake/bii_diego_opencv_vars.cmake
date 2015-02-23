
# LIBRARY diego_opencv ##################################
# with interface diego_opencv_interface

# Source code files of the library
SET(BII_LIB_SRC  opencv/cv.h
			opencv/highgui.h
			opencv2/calib3d/calib3d.hpp
			opencv2/core/affine.hpp
			opencv2/core/core.hpp
			opencv2/core/core_c.h
			opencv2/core/eigen.hpp
			opencv2/core/internal.hpp
			opencv2/core/mat.hpp
			opencv2/core/operations.hpp
			opencv2/core/types_c.h
			opencv2/core/version.hpp
			opencv2/features2d/features2d.hpp
			opencv2/flann/all_indices.h
			opencv2/flann/allocator.h
			opencv2/flann/any.h
			opencv2/flann/autotuned_index.h
			opencv2/flann/composite_index.h
			opencv2/flann/config.h
			opencv2/flann/defines.h
			opencv2/flann/dist.h
			opencv2/flann/dynamic_bitset.h
			opencv2/flann/flann.hpp
			opencv2/flann/flann_base.hpp
			opencv2/flann/general.h
			opencv2/flann/ground_truth.h
			opencv2/flann/heap.h
			opencv2/flann/hierarchical_clustering_index.h
			opencv2/flann/index_testing.h
			opencv2/flann/kdtree_index.h
			opencv2/flann/kdtree_single_index.h
			opencv2/flann/kmeans_index.h
			opencv2/flann/linear_index.h
			opencv2/flann/logger.h
			opencv2/flann/lsh_index.h
			opencv2/flann/lsh_table.h
			opencv2/flann/matrix.h
			opencv2/flann/miniflann.hpp
			opencv2/flann/nn_index.h
			opencv2/flann/params.h
			opencv2/flann/random.h
			opencv2/flann/result_set.h
			opencv2/flann/sampling.h
			opencv2/flann/saving.h
			opencv2/flann/timer.h
			opencv2/highgui/highgui.hpp
			opencv2/highgui/highgui_c.h
			opencv2/imgproc/imgproc.hpp
			opencv2/imgproc/imgproc_c.h
			opencv2/imgproc/types_c.h
			opencv2/legacy/compat.hpp
			opencv2/objdetect/objdetect.hpp
			opencv2/video/tracking.hpp)
# STATIC by default if empty, or SHARED
SET(BII_LIB_TYPE )
# Dependencies to other libraries (user2_block2, user3_blockX)
SET(BII_LIB_DEPS diego_opencv_interface )
# System included headers
SET(BII_LIB_SYSTEM_HEADERS algorithm assert.h cassert cmath complex cstddef cstdio cstdlib cstring deque emmintrin.h float.h immintrin.h intrin.h iomanip iostream limits limits.h map math.h new nmmintrin.h ostream pmmintrin.h pthread.h set smmintrin.h sstream stdarg.h stddef.h stdexcept stdint.h stdio.h stdlib.h string string.h time.h tmmintrin.h typeinfo unordered_map vector)
# Required include paths
SET(BII_LIB_INCLUDE_PATHS ${CMAKE_HOME_DIRECTORY}/../deps/diego/opencv//)


# Executables to be created
SET(BII_BLOCK_EXES )

