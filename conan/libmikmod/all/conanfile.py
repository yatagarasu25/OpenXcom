from conan import ConanFile, tools
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.apple import is_apple_os
from conan.tools.files import get, patch, replace_in_file, rmdir, copy
import os


class LibmikmodConan(ConanFile):
    name = "libmikmod"
    version = "3.3.11.1"
    description = "Module player and library supporting many formats, including mod, s3m, it, and xm."
    topics = ("libmikmod", "audio")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://mikmod.sourceforge.net"
    license = "LGPL-2.1-or-later"
    exports_sources = ["patches/*", "CMakeLists.txt"]

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_dsound": [True, False],
        "with_mmsound": [True, False],
        "with_alsa": [True, False],
        "with_oss": [True, False],
        "with_pulse": [True, False],
        "with_coreaudio": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_dsound": True,
        "with_mmsound": True,
        "with_alsa": True,
        "with_oss": True,
        "with_pulse": True,
        "with_coreaudio": True
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            del self.options.with_dsound
            del self.options.with_mmsound
        if self.settings.os != "Linux":
            del self.options.with_alsa
        # Non-Apple Unices
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_oss
            del self.options.with_pulse
        # Apple
        if is_apple_os(self):
            del self.options.with_coreaudio

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.settings.os == "Linux":
            if self.options.with_alsa:
                self.requires("libalsa/1.2.7.2")
            if self.options.with_pulse:
                self.requires("pulseaudio/14.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

        for p in self.conan_data.get("patches", {}).get(self.version, []):
            patch(self, **p)

        replace_in_file(self, "CMakeLists.txt",
                              "CMAKE_SOURCE_DIR",
                              "PROJECT_SOURCE_DIR")

         # Ensure missing dependencies yields errors
        replace_in_file(self, "CMakeLists.txt",
                              "MESSAGE(WARNING",
                              "MESSAGE(FATAL_ERROR")

        replace_in_file(self, os.path.join("drivers", "drv_alsa.c"),
                              "alsa_pcm_close(pcm_h);",
                              "if (pcm_h) alsa_pcm_close(pcm_h);")


    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MYVAR"] = "1"
        tc.preprocessor_definitions["MYDEFINE"] = "2"
        tc.preprocessor_definitions["ENABLE_STATIC"] = not self.options.shared
        tc.preprocessor_definitions["ENABLE_DOC"] = False
        tc.preprocessor_definitions["ENABLE_DSOUND"] = self.options.get_safe("with_dsound", False)
        tc.preprocessor_definitions["ENABLE_MMSOUND"] = self.options.get_safe("with_mmsound", False)
        tc.preprocessor_definitions["ENABLE_ALSA"] = self.options.get_safe("with_alsa", False)
        tc.preprocessor_definitions["ENABLE_OSS"] = self.options.get_safe("with_oss", False)
        tc.preprocessor_definitions["ENABLE_PULSE"] = self.options.get_safe("with_pulse", False)
        tc.preprocessor_definitions["ENABLE_COREAUDIO"] = self.options.get_safe("with_coreaudio", False)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.verbose = True
        cmake.configure()
        cmake.build()

    def package(self):
        #copy(self, pattern="COPYING.LESSER", dst="licenses", src=self._source_subfolder)
        cmake = CMake(self)
        cmake.install()
        os.remove(os.path.join(self.package_folder, "bin", "libmikmod-config"))
        if not self.options.shared:
            rmdir(self, os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = [ "mikmod" ]
        if not self.options.shared:
            self.cpp_info.defines = ["MIKMOD_STATIC"]
        self.cpp_info.filenames["pkg_config"] = "mikmod"

        if self.options.get_safe("with_dsound"):
            self.cpp_info.system_libs.append("dsound")
        if self.options.get_safe("with_mmsound"):
            self.cpp_info.system_libs.append("winmm")
        if self.options.get_safe("with_coreaudio"):
            self.cpp_info.frameworks.append("CoreAudio")
