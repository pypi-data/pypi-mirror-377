# BSD 3-Clause License
#
# Copyright (c) 2025, Shahriar Rezghi <shahriar.rezghi.sh@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Project
cmake_minimum_required(VERSION 3.12)
project(Blasw VERSION 0.1.0 LANGUAGES CXX)

include(GNUInstallDirs)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Variables
set(BLASW_MASTER OFF CACHE INTERNAL "")
if(CMAKE_CURRENT_SOURCE_DIR STREQUAL CMAKE_SOURCE_DIR)
  set(BLASW_MASTER ON CACHE INTERNAL "")
endif()

# Variables to Control the Backend Library (if not using the BLASW_BACKEND variables below):
#  BLAS Variables:
#   BLA_STATIC: BOOL -> Static Linkage for the BLAS Library
#   BLA_VENDOR: STRING -> Provider of the BLAS Library
#   BLAS_ROOT: PATH -> Root Directory for the BLAS library
#  MKL Variables
#   MKL_LINK: STRING -> Linking Type to use for MKL (static, dynamic, sdl)
#   MKL_ARCH: STRING -> Architecture to use for MKL (intel64)
#   MKL_INTERFACE: STRING -> Interface to use for MKL (lp64, ilp64)
#   MKL_THREADING: STRING -> Threading to use for MKL (sequential, intel_thread, gnu_thread, tbb_thread)
#   MKL_ROOT: PATH -> Root Directory for MKL

option(BLASW_INSTALL "Install BLASW Library" ${BLASW_MASTER})
option(BLASW_TESTS "Build BLASW Tests" ${BLASW_MASTER})
option(BLASW_FORCE_MKL "Force MKL for BLAS Backend" OFF)

set(BLASW_BACKEND_ROOT "" CACHE PATH
  "Root directory of the BLAS/MKL backend (applies to BLAS_ROOT/MKL_ROOT if they are not already set)")
set(BLASW_BACKEND_STATIC "" CACHE STRING
  "Static linking preference for BLAS/MKL: set to ON, OFF, or leave empty to not modify backend variables")
set(BLASW_BACKEND_PROVIDER "" CACHE STRING
  "Provider string. Either 'mkl-<arch>-<interface>-<threading>' (e.g. mkl-intel64-lp64-intel_thread) or a CMake BLA_VENDOR (e.g. OpenBLAS, FlexiBLAS, ATLAS, Apple)")

if(DEFINED CACHE{BLASW_BACKEND_STATIC} AND NOT BLASW_BACKEND_STATIC STREQUAL "")
  if(BLASW_BACKEND_STATIC STREQUAL "ON" OR BLASW_BACKEND_STATIC)
    if(NOT DEFINED CACHE{BLA_STATIC})
      set(BLA_STATIC ON CACHE BOOL "Use static BLAS libraries")
    endif()
    if(NOT DEFINED CACHE{MKL_LINK})
      set(MKL_LINK static CACHE STRING "MKL linking type (static/dynamic)")
    endif()
  elseif(BLASW_BACKEND_STATIC STREQUAL "OFF")
    if(NOT DEFINED CACHE{BLA_STATIC})
      set(BLA_STATIC OFF CACHE BOOL "Use static BLAS libraries")
    endif()
    if(NOT DEFINED CACHE{MKL_LINK})
      set(MKL_LINK dynamic CACHE STRING "MKL linking type (static/dynamic)")
    endif()
  else()
    message(WARNING "BLASW_BACKEND_STATIC set to '${BLASW_BACKEND_STATIC}' (expected ON/OFF). Ignoring.")
  endif()
endif()

if(DEFINED CACHE{BLASW_BACKEND_ROOT} AND BLASW_BACKEND_ROOT)
  if(NOT DEFINED CACHE{BLAS_ROOT})
    set(BLAS_ROOT "${BLASW_BACKEND_ROOT}" CACHE PATH "BLAS root directory")
  endif()
  if(NOT DEFINED CACHE{MKL_ROOT})
    set(MKL_ROOT "${BLASW_BACKEND_ROOT}" CACHE PATH "MKL root directory")
  endif()
endif()

if(DEFINED CACHE{BLASW_BACKEND_PROVIDER} AND NOT BLASW_BACKEND_PROVIDER STREQUAL "")
  string(TOLOWER "${BLASW_BACKEND_PROVIDER}" _blasw_provider_lc)
  string(REGEX MATCH "^mkl-([^-]+)-([^-]+)-([^-]+)$" _is_mkl "${_blasw_provider_lc}")

  if(_is_mkl)
    if(NOT DEFINED CACHE{MKL_ARCH})
      set(MKL_ARCH "${CMAKE_MATCH_1}" CACHE STRING "MKL architecture")
    endif()
    if(NOT DEFINED CACHE{MKL_INTERFACE})
      set(MKL_INTERFACE "${CMAKE_MATCH_2}" CACHE STRING "MKL interface (lp64/ilp64)")
    endif()
    if(NOT DEFINED CACHE{MKL_THREADING})
      set(MKL_THREADING "${CMAKE_MATCH_3}" CACHE STRING "MKL threading (sequential/intel_thread/tbb_thread)")
    endif()
  else()
    if(NOT DEFINED CACHE{BLA_VENDOR})
      set(BLA_VENDOR "${BLASW_BACKEND_PROVIDER}" CACHE STRING "Preferred BLAS vendor")
    endif()
  endif()
endif()

# Files
configure_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/src/blasw/config.h.in"
  "${CMAKE_CURRENT_BINARY_DIR}/gen/blasw/config.h"
  @ONLY)
set(BLASW_HEADERS
  "${CMAKE_CURRENT_SOURCE_DIR}/src/blasw/blasw.h"
  "${CMAKE_CURRENT_BINARY_DIR}/gen/blasw/config.h")
list(APPEND CMAKE_MODULE_PATH
  "${CMAKE_CURRENT_LIST_DIR}/cmake/")

# Library
find_package(CBLAS REQUIRED)
find_package(LAPACKE QUIET)

add_library(BLASW INTERFACE)
target_link_libraries(BLASW INTERFACE
  CBLAS::CBLAS
  $<$<TARGET_EXISTS:LAPACKE::LAPACKE>:LAPACKE::LAPACKE>)
target_include_directories(BLASW INTERFACE
  "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/>"
  "$<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}/gen/>"
  "$<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>")
add_library(BLASW::BLASW ALIAS BLASW)

if(BLASW_TESTS)
  add_executable(BlaswTests test/tests.cpp ${BLASW_HEADERS})
  target_link_libraries(BlaswTests PRIVATE BLASW::BLASW)
endif()

# Installation
if(BLASW_INSTALL)
  include(CMakePackageConfigHelpers)

  write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/BLASWConfigVersion.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY AnyNewerVersion)
  configure_package_config_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/BLASWConfig.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/BLASWConfig.cmake"
    INSTALL_DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/BLASW")

  install(FILES ${BLASW_HEADERS}
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/blasw)
  install(TARGETS BLASW
    EXPORT  BLASWTargets
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
  install(EXPORT BLASWTargets
    NAMESPACE BLASW::
    DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/BLASW")
  install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/BLASWConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/BLASWConfigVersion.cmake"
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/FindCBLAS.cmake"
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/FindLAPACKE.cmake"
    DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/BLASW")

  export(EXPORT BLASWTargets
    NAMESPACE BLASW::
    FILE "${CMAKE_CURRENT_BINARY_DIR}/BLASWTargets.cmake")
endif()
