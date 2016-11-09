project(tst_libxslt)
cmake_minimum_required(VERSION 2.8.12)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(tst_libxslt libxslt.cpp)
target_link_libraries(tst_libxslt ${CONAN_LIBS})
