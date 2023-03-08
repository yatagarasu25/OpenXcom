from conan import ConanFile, tools
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, patch, save

class SdlGfxConan(ConanFile):
   name = "sdl_gfx"
   version = "2.0.25"
   settings = "os", "compiler", "build_type", "arch"
   requires = "sdl/1.2.15"
#   default_options = {"poco:shared": True, "openssl:shared": True}

   def source(self):
      #get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self.source_folder)
      #get(self, "https://sourceforge.net/projects/sdlgfx/files/SDL_gfx-2.0.25.tar.gz", strip_root=True)
      get(self, **self.conan_data["sources"][self.version], strip_root=True)

      save(self, "conanfile.txt", """[requires]
sdl/1.2.15

[generators]
CMakeDeps
CMakeToolchain
""")
      save(self, "CMakeLists.txt", """cmake_minimum_required(VERSION 3.1)
project(sdl_gfx)

execute_process(COMMAND conan install --update --build=missing ${CMAKE_SOURCE_DIR} -s build_type=${CMAKE_BUILD_TYPE})

include(GNUInstallDirs)

find_package(SDL REQUIRED)

add_library(${PROJECT_NAME} STATIC
    SDL_framerate.c
    SDL_gfxBlitFunc.c
    SDL_gfxPrimitives.c
    SDL_imageFilter.c
    SDL_rotozoom.c
)
target_link_libraries(${PROJECT_NAME} SDL::SDL)

install(TARGETS ${PROJECT_NAME} EXPORT ${PROJECT_NAME}Targets
        LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
        ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
        RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}")

install(EXPORT ${PROJECT_NAME}Targets
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
        NAMESPACE ${PROJECT_NAME}::)

install(FILES SDL_framerate.h SDL_gfxBlitFunc.h SDL_gfxPrimitives.h SDL_gfxPrimitives_font.h SDL_imageFilter.h SDL_rotozoom.h
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
""")
      patch(self, patch_string="""diff --git ./SDL_gfxPrimitives.c ./SDL_gfxPrimitives.patched
index c77d8b5..8bd70c2 100644
--- ./SDL_gfxPrimitives.c
+++ ./SDL_gfxPrimitives.patched
@@ -3960,7 +3960,7 @@ int ellipseRGBA(SDL_Surface * dst, Sint16 x, Sint16 y, Sint16 rx, Sint16 ry, Uin
 /* ----- AA Ellipse */
 
 /* Windows targets do not have lrint, so provide a local inline version */
-#if defined(_MSC_VER)
+#if defined(_MSC_VER) && _MSC_VER < 1928
 /* Detect 64bit and use intrinsic version */
 #ifdef _M_X64
 #include <emmintrin.h>
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
      self.cpp_info.libs = [ "sdl_gfx" ]
      self.cpp_info.includedirs = [ "include" ]

   def package(self):
      cmake = CMake(self)
      cmake.install()
