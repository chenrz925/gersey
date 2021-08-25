cmake_minimum_required(VERSION 3.4...3.18)
project(geyser)
set(CMAKE_CXX_STANDARD 17)

add_subdirectory(pybind11)
add_subdirectory(fmt)

aux_source_directory(src GEYSER_SOURCES)
pybind11_add_module(geyser ${GEYSER_SOURCES})

# EXAMPLE_VERSION_INFO is defined by setup.py and passed into the C++ code as a
# define (VERSION_INFO) here.
target_compile_definitions(geyser PRIVATE VERSION_INFO=${GEYSER_VERSION_INFO})
target_link_libraries(geyser PRIVATE fmt::fmt)
