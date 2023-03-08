from conan import ConanFile, tools
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, rmdir, save, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os
import functools


class SDLMixerConan(ConanFile):
    name = "sdl_mixer"
    version = "1.2.12"
    description = "SDL_mixer is a sample multi-channel audio mixer library"
    topics = ("sdl_mixer", "sdl2", "sdl", "mixer", "audio", "multimedia", "sound", "music")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libsdl.org/projects/SDL_mixer/"
    license = "Zlib"
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "cmd": [True, False],
               "wav": [True, False],
               "flac": [True, False],
               "mpg123": [True, False],
               "mad": [True, False],
               "ogg": [True, False],
               "opus": [True, False],
               "mikmod": [True, False],
               "modplug": [True, False],
               "fluidsynth": [True, False],
               "nativemidi": [True, False],
               "tinymidi": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "cmd": False,  # needs sys/wait.h
                       "wav": True,
                       "flac": True,
                       "mpg123": True,
                       "mad": True,
                       "ogg": True,
                       "opus": True,
                       "mikmod": True,
                       "modplug": True,
                       "fluidsynth": False, # TODO: add fluidsynth to Conan Center
                       "nativemidi": True,
                       "tinymidi": True}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.tinymidi
        else:
            del self.options.nativemidi

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.options.shared:
            del self.options.fPIC
#        del self.settings.compiler.libcxx
#        del self.settings.compiler.cppstd

    def requirements(self):
        if Version(self.version) >= "2.0.0":
            self.requires("sdl/2.0.20")
            if self.options.flac:
                self.requires("flac/1.3.3")
            if self.options.mpg123:
                self.requires("mpg123/1.29.3")
            if self.options.mad:
                self.requires("libmad/0.15.1b")
            if self.options.ogg:
                self.requires("ogg/1.3.5")
                self.requires("vorbis/1.3.7")
            if self.options.opus:
                self.requires("openssl/1.1.1q")
                self.requires("opus/1.3.1")
                self.requires("opusfile/0.12")
            if self.options.mikmod:
                self.requires("libmikmod/3.3.11.1")
            if self.options.modplug:
                self.requires("libmodplug/0.8.9.0")
            if self.options.fluidsynth:
                self.requires("fluidsynth/2.2") # TODO: this package is missing on the conan-center-index
            if self.settings.os == "Linux":
                if self.options.tinymidi:
                    self.requires("tinymidi/cci.20130325")
        else:
            self.requires("sdl/1.2.15")
            self.requires("smpeg/0.4.5")
            if self.options.flac:
                self.requires("flac/1.3.3")
            if self.options.ogg:
                self.requires("ogg/1.3.5")
                self.requires("vorbis/1.3.7")
            if self.options.mikmod:
                self.requires("libmikmod/3.3.11.1")

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

        rmdir(self, os.path.join(self.folders.source, "external"))

        if Version(self.version) < "2.0.0":
            save(self, os.path.join(self.source_folder, "conanfile.txt"), """[requires]
sdl/1.2.15
smpeg/0.4.5
flac/1.3.3
ogg/1.3.5
vorbis/1.3.7
libmikmod/3.3.11.1

[generators]
CMakeDeps
CMakeToolchain
""")
            save(self, os.path.join(self.source_folder, "CMakeLists.txt"), """cmake_minimum_required(VERSION 3.1)
project(sdl_mixer)

execute_process(COMMAND conan install --update --build=missing ${CMAKE_SOURCE_DIR} -s build_type=${CMAKE_BUILD_TYPE})

include(GNUInstallDirs)

find_package(SDL REQUIRED)
find_package(smpeg REQUIRED)
find_package(libmikmod REQUIRED)
find_package(Ogg REQUIRED)
find_package(vorbis REQUIRED)
find_package(flac REQUIRED)

file(GLOB SDL_SOURCES "*.c"
#    "mikmod/*.c"
    "native_midi_gpl/*.c"
    "timidity/*.c")


add_library(${PROJECT_NAME} STATIC
    native_midi/native_midi_win32.c
    native_midi/native_midi_common.c
    ${SDL_SOURCES}
)
target_link_libraries(${PROJECT_NAME} SDL::SDL)
target_link_libraries(${PROJECT_NAME} smpeg::smpeg)
#if(${WAV_MUSIC})
#target_link_libraries(${PROJECT_NAME} SDL::SDL)
#endif()
#if(${MOD_MUSIC})
target_link_libraries(${PROJECT_NAME} libmikmod::libmikmod)
#endif()
#if(${OGG_MUSIC})
target_link_libraries(${PROJECT_NAME} Ogg::ogg)
target_link_libraries(${PROJECT_NAME} Vorbis::vorbis)
#endif()
#if(${FLAC_MUSIC})
target_link_libraries(${PROJECT_NAME} flac::flac)
#endif()
#if(${MID_MUSIC})
#endif()

target_include_directories(${PROJECT_NAME}
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/timidity>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/native_midi>)

#target_include_directories(${PROJECT_NAME}
#    PUBLIC
#        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
#        $<INSTALL_INTERFACE:include>
#)

install(TARGETS ${PROJECT_NAME} EXPORT ${PROJECT_NAME}Targets
        LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
        ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
        RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}")

install(EXPORT ${PROJECT_NAME}Targets
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
        NAMESPACE ${PROJECT_NAME}::)

install(FILES SDL_mixer.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
""")

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) >= "2.0.0":
            tc.preprocessor_definitions["CMD"] = self.options.cmd
            tc.preprocessor_definitions["WAV"] = self.options.wav
            tc.preprocessor_definitions["FLAC"] = self.options.flac
            tc.preprocessor_definitions["MP3_MPG123"] = self.options.mpg123
            tc.preprocessor_definitions["MP3_MAD"] = self.options.mad
            tc.preprocessor_definitions["OGG"] = self.options.ogg
            tc.preprocessor_definitions["OPUS"] = self.options.opus
            tc.preprocessor_definitions["MOD_MIKMOD"] = self.options.mikmod
            tc.preprocessor_definitions["MOD_MODPLUG"] = self.options.modplug
            tc.preprocessor_definitions["MID_FLUIDSYNTH"] = self.options.fluidsynth
            if self.settings.os == "Linux":
                tc.preprocessor_definitions["MID_TINYMIDI"] = self.options.tinymidi
                tc.preprocessor_definitions["MID_NATIVE"] = False
            else:
                tc.preprocessor_definitions["MID_TINYMIDI"] = False
                tc.preprocessor_definitions["MID_NATIVE"] = self.options.nativemidi

            tc.preprocessor_definitions["FLAC_DYNAMIC"] = self.options["flac"].shared if self.options.flac else False
            tc.preprocessor_definitions["MP3_MPG123_DYNAMIC"] = self.options["mpg123"].shared if self.options.mpg123 else False
            tc.preprocessor_definitions["OGG_DYNAMIC"] = self.options["ogg"].shared if self.options.ogg else False
            tc.preprocessor_definitions["OPUS_DYNAMIC"] = self.options["opus"].shared if self.options.opus else False
            tc.preprocessor_definitions["MOD_MIKMOD_DYNAMIC"] = self.options["libmikmod"].shared if self.options.mikmod else False
            tc.preprocessor_definitions["MOD_MODPLUG_DYNAMIC"] = self.options["libmodplug"].shared if self.options.modplug else False
        else:
            tc.preprocessor_definitions["WAV_MUSIC"] = self.options.wav
            tc.preprocessor_definitions["MOD_MUSIC"] = self.options.mikmod
            #tc.preprocessor_definitions["MOD_DYNAMIC"] = self.options["libmikmod"].shared if self.options.mikmod else False
            tc.preprocessor_definitions["OGG_MUSIC"] = self.options.ogg
            #tc.preprocessor_definitions["OGG_DYNAMIC"] = self.options["ogg"].shared if self.options.ogg else False
            tc.preprocessor_definitions["FLAC_MUSIC"] = self.options.flac
            #tc.preprocessor_definitions["FLAC_DYNAMIC"] = self.options["flac"].shared if self.options.flac else False
            tc.preprocessor_definitions["MP3_MUSIC"] = False
            #MP3_DYNAMIC=\&quot;smpeg.dll\&quot;;
            tc.preprocessor_definitions["MID_MUSIC"] = True
            tc.preprocessor_definitions["USE_TIMIDITY_MIDI"] = False # self.options.tinymidi
            tc.preprocessor_definitions["USE_NATIVE_MIDI"] = self.options.nativemidi

        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        cmake = CMake(self)
        cmake.verbose = True
        cmake.configure()
        cmake.build()

    def package(self):
        #copy(pattern="COPYING.txt", dst="licenses", src=self.folders.source)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        if Version(self.version) >= "2.0.0":
            self.cpp_info.set_property("pkg_config_name", "SDL2_mixer")
            self.cpp_info.set_property("cmake_file_name", "SDL2_mixer")
            self.cpp_info.set_property("cmake_target_name", "SDL2_mixer::SDL2_mixer")
            self.cpp_info.set_property("pkg_config_name", "SDL2_mixer")
            self.cpp_info.libs = ["SDL2_mixer"]

            self.cpp_info.names["cmake_find_package"] = "SDL2_mixer"
            self.cpp_info.names["cmake_find_package_multi"] = "SDL2_mixer"
        else:
            self.cpp_info.set_property("pkg_config_name", "SDL_mixer")
            self.cpp_info.set_property("cmake_file_name", "SDL_mixer")
            self.cpp_info.set_property("cmake_target_name", "SDL_mixer::SDL_mixer")
            self.cpp_info.set_property("pkg_config_name", "SDL_mixer")
            self.cpp_info.libs = ["SDL_mixer"]

            self.cpp_info.names["cmake_find_package"] = "SDL_mixer"
            self.cpp_info.names["cmake_find_package_multi"] = "SDL_mixer"
