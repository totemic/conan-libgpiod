import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools


class LibgpiodConan(ConanFile):
    name = "libgpiod"
    version = "1.4.1"
    license = "LGPL-2.1-or-later"
    homepage = "https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git"
    url = "https://github.com/jens-totemic/conan-libgpiod"
    description = "Library for interacting with the linux GPIO character device"
    topics = ("gpio")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _source_subfolder = "sources"

    # def source(self):
    #     git = tools.Git(folder="libgpiod")
    #     git.clone("https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git", "v" + self.version)

    def source(self):
        release_name = "%s-%s" % (self.name, self.version)
        unpacked_name = release_name
        tools.get("{0}/snapshot/{1}.tar.gz".format(self.homepage, release_name),
                  sha256="7cd9fc7efe9a689e2852f907a4f79399f7488a32ae57555f3be432b0c2c80a75")
        os.rename(unpacked_name, self._source_subfolder)

    # def build_requirements(self):
    #     installer = tools.SystemPackageTool()
    #     installer.install("autoconf-archive")

    def build(self):
        if self.settings.os == "Linux":
            self.run("autoreconf --force --install --verbose", cwd=self._source_subfolder)
            cfgArgs = ["--enable-bindings-cxx"]
            cfgArgs += ["--enable-tools"]
            if self.options.shared:
                cfgArgs += ["--enable-shared", "--disable-static"]
            else:
                cfgArgs += ["--disable-shared", "--enable-static"]
            with tools.chdir(self._source_subfolder):
                autotools = AutoToolsBuildEnvironment(self)
                envVars = autotools.vars
                # fixes error "undefined reference to `rpl_malloc'"
                envVars["ac_cv_func_malloc_0_nonnull"] = "yes"
                #autotools.configure(configure_dir="libgpiod", args=cfgArgs, vars=envVars)
                autotools.configure(args=cfgArgs, vars=envVars)
                autotools.make()
                autotools.install()

        else:
            # We allow using it on all platforms, but for anything except Linux nothing is produced
            # this allows unconditionally including this conan package on all platforms
            self.output.info("Nothing to be done for this OS")

    def package(self):
        if self.settings.os == "Linux":
            # self.copy(pattern="COPYING", src="libgpiod", keep_path=False)
            # self.copy("*.h", dst="include", src="libgpiod/include")
            # self.copy("*.hpp", dst="include", src="libgpiod/bindings/cxx")
            # self.copy("*.so", dst="lib", keep_path=False)
            # self.copy("*.a", dst="lib", keep_path=False)
            with tools.chdir(self._source_subfolder):
                autotools = AutoToolsBuildEnvironment(self)
                autotools.install()
        else:
            # on non-linux platforms, expose the header files to help cross-development
            self.copy(pattern="*.h", dst="include", src=self._source_subfolder+"/include", symlinks=True)
            self.copy(pattern="*.hpp", dst="include", src=self._source_subfolder+"/bindings/cxx", symlinks=True)

    def package_info(self):
        if self.settings.os == "Linux":
            self.cpp_info.libs = ["gpiodcxx", "gpiod"]
