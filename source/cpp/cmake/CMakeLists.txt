PROJECT( cpp )
cmake_minimum_required(VERSION 3.0)

# inclusion of general biicode macros, biicode.cmake 
set(CMAKE_MODULE_PATH "${CMAKE_HOME_DIRECTORY}/cmake"
					  "${CMAKE_HOME_DIRECTORY}/../blocks"
					  "${CMAKE_HOME_DIRECTORY}/../deps")
INCLUDE(biicode.cmake) 

ADD_DEFINITIONS(-DBIICODE)
SET(BIICODE_ENV_DIR /Users/smalus/.biicode)

#artifact to allow upstream configurations
BII_PREBUILD_STEP(deps/diego/opencv)
BII_PREBUILD_STEP(blocks/smalus/simpleOCRExample)

enable_testing()
# Inclusion of the blocks affected by the build
BII_INCLUDE_BLOCK(deps/diego/opencv)
BII_INCLUDE_BLOCK(blocks/smalus/simpleOCRExample)
