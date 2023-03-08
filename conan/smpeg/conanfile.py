from conan import ConanFile, tools
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, patch, save

class SdlGfxConan(ConanFile):
   name = "smpeg"
   version = "0.4.5"
   settings = "os", "compiler", "build_type", "arch"
   requires = "sdl/[>=1.2.0]"
#   default_options = {"poco:shared": True, "openssl:shared": True}

   def source(self):
      get(self, **self.conan_data["sources"][self.version], strip_root=True)

      save(self, "conanfile.txt", """[requires]
sdl/1.2.0

[generators]
CMakeDeps
CMakeToolchain
""")
      save(self, "CMakeLists.txt", """cmake_minimum_required(VERSION 3.1)
project(smpeg)

execute_process(COMMAND conan install --update --build=missing ${CMAKE_SOURCE_DIR} -s build_type=${CMAKE_BUILD_TYPE})

include(GNUInstallDirs)

find_package(SDL REQUIRED)

add_library(${PROJECT_NAME} STATIC
#    glmovie-tile.c
#    glmovie.c
#    gtv.c
    MPEGfilter.c
    plaympeg.c
    MPEG.cpp
    MPEGlist.cpp
    MPEGring.cpp
    MPEGstream.cpp
    MPEGsystem.cpp
    smpeg.cpp
)
target_link_libraries(${PROJECT_NAME} SDL::SDL)

install(TARGETS ${PROJECT_NAME} EXPORT ${PROJECT_NAME}Targets
        LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
        ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
        RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}")

install(EXPORT ${PROJECT_NAME}Targets
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
        NAMESPACE ${PROJECT_NAME}::)

install(FILES smpeg.h MPEGvideo.h MPEGsystem.h MPEGstream.h MPEGring.h MPEGlist.h MPEGfilter.h MPEGaudio.h MPEGerror.h MPEGaction.h MPEG.h 
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
""")

   def imports(self):
      self.copy("*.dll", dst="bin", src="bin")
      self.copy("*.dylib*", dst="bin", src="lib")

   def layout(self):
      cmake_layout(self)

   def generate(self):
      tc = CMakeToolchain(self)
      tc.generate()
      cd = CMakeDeps(self)
      cd.generate()

   def build(self):
      cmake = CMake(self)
      cmake.verbose = True
      cmake.configure()
      cmake.build()


   def package_info(self):
      self.cpp_info.libs = [ "smpeg" ]
      self.cpp_info.includedirs = [ "include" ]

   def package(self):
      cmake = CMake(self)
      cmake.install()
