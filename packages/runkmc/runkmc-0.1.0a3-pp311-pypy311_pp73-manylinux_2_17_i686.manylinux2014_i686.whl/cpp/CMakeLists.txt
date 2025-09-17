cmake_minimum_required(VERSION 3.15)
project(RunKMC)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include directories
include_directories(include)
include_directories(include/runkmc)
include_directories(include/runkmc/kmc)
include_directories(include/eigen-3.4.0)

add_executable(RunKMC src/RunKMC.cpp)

target_compile_options(RunKMC PRIVATE -O3)
