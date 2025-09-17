#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "Halide::Python" for configuration "Release"
set_property(TARGET Halide::Python APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(Halide::Python PROPERTIES
  IMPORTED_COMMON_LANGUAGE_RUNTIME_RELEASE ""
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/./halide_.cpython-313-darwin.so"
  IMPORTED_NO_SONAME_RELEASE "TRUE"
  )

list(APPEND _cmake_import_check_targets Halide::Python )
list(APPEND _cmake_import_check_files_for_Halide::Python "${_IMPORT_PREFIX}/./halide_.cpython-313-darwin.so" )

# Import target "Halide::PyStubs" for configuration "Release"
set_property(TARGET Halide::PyStubs APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(Halide::PyStubs PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libHalidePyStubs.a"
  )

list(APPEND _cmake_import_check_targets Halide::PyStubs )
list(APPEND _cmake_import_check_files_for_Halide::PyStubs "${_IMPORT_PREFIX}/lib/libHalidePyStubs.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
