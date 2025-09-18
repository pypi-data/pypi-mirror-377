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

if(BLASW_FORCE_MKL)
    find_package(MKL CONFIG REQUIRED HINTS "$ENV{MKLROOT}")

    if(MKL_FOUND)
        set(CBLAS_FOUND TRUE)
        add_library(CBLAS::CBLAS INTERFACE IMPORTED)
        set_target_properties(CBLAS::CBLAS PROPERTIES
            INTERFACE_LINK_LIBRARIES
                "$<LINK_ONLY:MKL::MKL>"
            INTERFACE_INCLUDE_DIRECTORIES
                "$<TARGET_PROPERTY:MKL::MKL,INTERFACE_INCLUDE_DIRECTORIES>"
            INTERFACE_COMPILE_OPTIONS
                "$<TARGET_PROPERTY:MKL::MKL,INTERFACE_COMPILE_OPTIONS>"
            INTERFACE_COMPILE_DEFINITIONS
                "BLASW_CBLAS_FOUND;BLASW_CBLAS_MKL")
        set(CBLAS_MKL ON CACHE INTERNAL "")
    endif()
else()
    set(CBLAS_MKL OFF CACHE INTERNAL "")
    find_package(BLAS)

    if(BLAS_FOUND)
        include(CheckFunctionExists)
        set(CMAKE_REQUIRED_LIBRARIES ${BLAS_LIBRARIES})
        set(CMAKE_REQUIRED_FLAGS ${BLAS_LINKER_FLAGS})
        check_function_exists(cblas_saxpy TEMP_FOUND)

        if(TEMP_FOUND)
            set(CBLAS_LIBRARIES ${BLAS_LIBRARIES})
            set(CBLAS_LINKER_FLAGS ${BLAS_LINKER_FLAGS})

            foreach(TEMP_NAME ${BLAS_LIBRARIES})
                get_filename_component(TEMP_NAME "${TEMP_NAME}" NAME)
                if(TEMP_NAME MATCHES "libmkl.*.so|libmkl.*.a|mkl.*.lib|mkl.*.dll")
                    set(CBLAS_MKL ON CACHE INTERNAL "")
                endif()
            endforeach()
        endif()

        unset(TEMP_FOUND CACHE)
    endif()

    if(NOT CBLAS_LIBRARIES)
        find_library(CBLAS_LIBRARIES
            NAMES cblas
            PATHS ${BLASW_PATH} $ENV{BLASW_PATH}
            PATH_SUFFIXES lib lib64)
    endif()

    if(CBLAS_LIBRARIES)
        foreach(TEMP_DIR ${CBLAS_LIBRARIES})
            get_filename_component(TEMP_DIR "${TEMP_DIR}" DIRECTORY)
            list(APPEND HINT_PATH "${TEMP_DIR}/../")
        endforeach()
    endif()

    if(CBLAS_MKL)
        find_path(CBLAS_INCLUDE_DIRS
            NAMES mkl_cblas.h
            PATHS ${HINT_PATH} "$ENV{MKLROOT}"
            PATH_SUFFIXES include)
    endif()

    if((NOT CBLAS_INCLUDE_DIRS) OR
            (CBLAS_INCLUDE_DIRS STREQUAL "CBLAS_INCLUDE_DIRS-NOTFOUND"))
        find_path(CBLAS_INCLUDE_DIRS
            NAMES cblas.h
            PATHS ${HINT_PATH}
            PATH_SUFFIXES include)
    endif()

    unset(HINT_PATH)

    include(FindPackageHandleStandardArgs)
    find_package_handle_standard_args(
        CBLAS
        FOUND_VAR CBLAS_FOUND
        REQUIRED_VARS
        CBLAS_LIBRARIES
        CBLAS_INCLUDE_DIRS)

    if(CBLAS_FOUND AND NOT TARGET CBLAS::CBLAS)
        add_library(CBLAS::CBLAS INTERFACE IMPORTED)
        set_target_properties(CBLAS::CBLAS PROPERTIES
            INTERFACE_INCLUDE_DIRECTORIES "${CBLAS_INCLUDE_DIRS}"
            INTERFACE_LINK_LIBRARIES "${CBLAS_LIBRARIES}"
            INTERFACE_LINK_OPTIONS "${CBLAS_LINKER_FLAGS}"
            INTERFACE_COMPILE_DEFINITIONS BLASW_CBLAS_FOUND)

        if(CBLAS_MKL)
            target_compile_definitions(CBLAS::CBLAS INTERFACE BLASW_CBLAS_MKL)
        endif()
    endif()

    mark_as_advanced(CBLAS_INCLUDE_DIRS CBLAS_LIBRARIES)
endif()
