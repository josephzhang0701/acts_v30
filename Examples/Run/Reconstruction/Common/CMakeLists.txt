add_library(
  ActsExamplesRecTracksCommon SHARED
  RecTruthTracks.cpp
  RecCKFTracks.cpp
  SeedingExample.cpp
  HoughExample.cpp
  MeasurementsToSpacepoints.cpp
)
target_include_directories(
  ActsExamplesRecTracksCommon
  PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>)
target_link_libraries(
  ActsExamplesRecTracksCommon
  PUBLIC
    ActsExamplesFramework
    ActsExamplesCommon
    ActsExamplesUtilities
    ActsExamplesMagneticField
    ActsExamplesIoPerformance)
if(ACTS_BUILD_PLUGIN_ONNX)
  target_compile_definitions(
    ActsExamplesRecTracksCommon PUBLIC ACTS_PLUGIN_ONNX)
  target_link_libraries(
    ActsExamplesRecTracksCommon PUBLIC ActsPluginOnnx)
endif()

install(
  TARGETS ActsExamplesRecTracksCommon
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})
