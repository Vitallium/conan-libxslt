from conans import ConanFile, ConfigureEnvironment
import os, codecs, re
from conans.tools import download, untargz, cpu_count, os_info

class LibxsltConan(ConanFile):
    name = "libxslt"
    version = "1.1.29"
    url = "http://github.com/vitallium/conan-libxslt"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    src_dir = "libxslt-%s" % version
    license = "https://git.gnome.org/browse/libxslt/tree/Copyright"
    requires = "libxml2/2.9.4@vitallium/testing"

    def source(self):
        tar_name = "libxslt-%s.tar.gz" % self.version
        url = "http://xmlsoft.org/sources/" + tar_name
        download(url, tar_name)
        untargz(tar_name)
        os.unlink(tar_name)

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            if self.options.shared and "MT" in str(self.settings.compiler.runtime):
                self.options.shared = False
            self.configure_options = "iconv=no xslt_debug=no debugger=no"
        else:
            self.configure_options = " \
                --without-python \
                --without-crypto \
                --without-debugger \
                --without-plugins \
                "

            if self.options.shared:
                self.configure_options += " --disable-static --enable-shared"
            else:
                self.configure_options += " --enable-static --disable-shared"

    def build(self):
        if self.settings.compiler == "Visual Studio":
            self.build_windows()
        else:
            self.build_with_configure()

    def build_windows(self):
        include_paths = ";".join(self.deps_cpp_info.include_paths)
        libs_paths = ";".join(self.deps_cpp_info.lib_paths)
        icu_libs = self.deps_cpp_info["icu"].libs
        icu_libs.append("wsock32")

        # add icu libs
        makefile_win_path = os.path.join(self.src_dir, "win32", "Makefile.msvc")
        encoding = self.detect_by_bom(makefile_win_path, "utf-8")
        patched_content = self.load(makefile_win_path, encoding)
        patched_content = re.sub("wsock32.lib", " ".join("%s.lib"%i for i in icu_libs), patched_content)
        self.save(makefile_win_path, patched_content)

        self.run('cd %s\win32 && cscript configure.js cruntime=/%s include=\"%s\" lib=\"%s" %s' % (
            self.src_dir,
            self.settings.compiler.runtime,
            include_paths,
            libs_paths,
            self.configure_options,
            ))
        self.run("cd %s\\win32 && nmake /f Makefile.msvc" % self.src_dir)

    def normalize_prefix_path(self, p):
        if os_info.is_windows:
            return p.replace('\\', '/')
        else:
            return p

    def build_with_configure(self):
        env = ConfigureEnvironment(self.deps_cpp_info, self.settings)
        command_env = env.command_line_env
        xml_config = self.normalize_prefix_path(self.deps_cpp_info["libxml2"].rootpath) + "/bin/xml2-config"

        if os_info.is_windows:
            command_env += " &&"
            command_env += ' set "XML_CONFIG=%s" &&' % xml_config
        else:
            command_env += ' XML_CONFIG="%s"' % xml_config

        self.run("%s sh %s/configure --prefix=%s %s" % (
            command_env,
            self.src_dir,
            self.normalize_prefix_path(self.package_folder),
            self.configure_options
            ))
        self.run("%s make -j %s" % (command_env, cpu_count()))
        self.run("%s make install" % command_env)

    def package(self):
        if self.settings.os != "Windows":
            return

        include_path = os.path.join(self.src_dir, "libxslt")
        self.copy("*.h", "include/libxslt", src=include_path, keep_path=True)

        if self.settings.os == "Windows":
            include_path = os.path.join(self.src_dir, "libexslt")
            self.copy("*.h", "include/libexslt", src=include_path, keep_path=True)

        self.copy(pattern="*.dll", dst="bin", src=self.src_dir, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=self.src_dir, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["libxslt"]

    # from https://github.com/SteffenL/conan-wxwidgets-custom/blob/master/conanfile.py#L260
    def load(self, path, encoding=None):
        encoding = detect_by_bom(path, "utf-8") if encoding is None else encoding
        with codecs.open(path, "rb", encoding=encoding) as f:
            return f.read()

    def save(self, path, content, encoding=None):
        with codecs.open(path, "wb", encoding=encoding) as f:
            f.write(content)

    # Ref.: http://stackoverflow.com/a/24370596
    def detect_by_bom(self,path,default):
        with open(path, 'rb') as f:
            raw = f.read(4)    #will read less if the file is smaller
        for enc,boms in \
                ('utf-8-sig',(codecs.BOM_UTF8,)),\
                ('utf-16',(codecs.BOM_UTF16_LE,codecs.BOM_UTF16_BE)),\
                ('utf-32',(codecs.BOM_UTF32_LE,codecs.BOM_UTF32_BE)):
            if any(raw.startswith(bom) for bom in boms): return enc
        return default
