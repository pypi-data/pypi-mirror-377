#----------------------------------------------------------------
# Generated CMake target import file for configuration "RELEASE".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "scalapack" for configuration "RELEASE"
set_property(TARGET scalapack APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(scalapack PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libscalapack.so"
  IMPORTED_SONAME_RELEASE "libscalapack.so"
  )

list(APPEND _cmake_import_check_targets scalapack )
list(APPEND _cmake_import_check_files_for_scalapack "${_IMPORT_PREFIX}/lib/libscalapack.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
