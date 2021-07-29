cmake_minimum_required(VERSION 3.19)
project(geyser LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 14)

find_package(pybind11 REQUIRED)

add_subdirectory(src)
