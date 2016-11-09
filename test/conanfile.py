from conans import ConanFile, CMake
import os

channel = os.getenv("CONAN_CHANNEL", "testing")
username = os.getenv("CONAN_USERNAME", "vitallium")

class DefaultNameConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    requires = "libxslt/1.1.29@%s/%s" % (username, channel)

    def build(self):
        cmake = CMake(self.settings)
        self.run("cmake %s %s" % (self.conanfile_directory, cmake.command_line))
        self.run("cmake --build . %s" % cmake.build_config)

    def imports(self):
        self.copy(pattern="*.dll", dst="bin", src="bin")

    def test(self):
        self.run(os.sep.join([".","bin", "tst_libxslt"]))