
# LIBRARY smalus_simpleOCRExample ##################################
# with interface smalus_simpleOCRExample_interface

# Source code files of the library
SET(BII_LIB_SRC  )
# STATIC by default if empty, or SHARED
SET(BII_LIB_TYPE )
# Dependencies to other libraries (user2_block2, user3_blockX)
SET(BII_LIB_DEPS smalus_simpleOCRExample_interface )
# System included headers
SET(BII_LIB_SYSTEM_HEADERS )
# Required include paths
SET(BII_LIB_INCLUDE_PATHS )


# Executables to be created
SET(BII_BLOCK_EXES main)



# EXECUTABLE main ##################################

SET(BII_main_SRC main.cpp)
SET(BII_main_DEPS smalus_simpleOCRExample_interface diego_opencv)
# System included headers
SET(BII_main_SYSTEM_HEADERS iostream)
# Required include paths
SET(BII_main_INCLUDE_PATHS )
