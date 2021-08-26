cmake_minimum_required(VERSION 3.4)
project(geyser)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE TRUE)
set(SPDLOG_FMT_EXTERNAL ON)
set(RAPIDJSON_BUILD_TESTS OFF)
set(RAPIDJSON_BUILD_EXAMPLES OFF)
set(RAPIDJSON_BUILD_DOC OFF)
set(YAML_BUILD_SHARED_LIBS OFF)

function(target_compiler_info target)
    target_compile_definitions(${target} PRIVATE GEYSER_VERSION_INFO=${GEYSER_VERSION_INFO})
    target_compile_definitions(${target} PRIVATE GEYSER_SYSTEM_NAME=${CMAKE_SYSTEM_NAME})
    target_compile_definitions(${target} PRIVATE GEYSER_SYSTEM_VERSION=${CMAKE_SYSTEM_VERSION})
    target_compile_definitions(${target} PRIVATE GEYSER_SYSTEM_PROCESSOR=${CMAKE_SYSTEM_PROCESSOR})
    target_compile_definitions(${target} PRIVATE GEYSER_COMPILER_NAME=${CMAKE_CXX_COMPILER_ID})
    target_compile_definitions(${target} PRIVATE GEYSER_COMPILER_VERSION=${CMAKE_CXX_COMPILER_VERSION})
endfunction()

function(target_link_libraries_common target)
    target_link_libraries(${target} PRIVATE fmt::fmt)
    target_link_libraries(${target} PRIVATE spdlog)
    target_link_libraries(${target} PRIVATE yaml-cpp)
endfunction()

add_subdirectory(pybind11)
add_subdirectory(fmt)
add_subdirectory(spdlog)
add_subdirectory(rapidjson)
add_subdirectory(yaml-cpp)

find_package(RapidJSON)
include_directories(include ${RapidJSON_INCLUDE_DIRS})
set(
        GEYSER_COMMON_SOURCES
        src/cli.cpp src/geyser.cpp src/logger.cpp src/profile.cpp
)
set(
        GEYSER_SOURCES
        ${GEYSER_COMMON_SOURCES} src/module.cpp
)
set(
        GUSH_SOURCES
        ${GEYSER_COMMON_SOURCES} src/main.cpp
)
pybind11_add_module(geyser ${GEYSER_SOURCES})
target_compiler_info(geyser)
target_link_libraries_common(geyser)

add_executable(gush ${GUSH_SOURCES})
target_compiler_info(gush)
target_link_libraries(gush PRIVATE pybind11::embed)
target_link_libraries_common(gush)

install(TARGETS gush RUNTIME DESTINATION ${CMAKE_SOURCE_DIR})