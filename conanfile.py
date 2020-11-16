import os
from os.path import join
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration


SOURCE_SUBFOLDER = "sources"


class LibgpiodConan(ConanFile):
    name = "libgpiod"
    version = "1.2.1"
    license = "LGPL-2.1-or-later"
    homepage = "https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git"
    url = "https://github.com/jens-totemic/conan-libgpiod"
    description = "Library for interacting with the linux GPIO character device"
    topics = ["gpio"]
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def configure(self):
        if self.settings.os != 'Linux':
            raise ConanInvalidConfiguration("Library is only supported for Linux")

    def source(self):
        release_name = f"{self.name}-{self.version}"
        download_url = f"{self.homepage}/snapshot/{release_name}.tar.gz"
        sha = "3a8578bd5257e36d0e69d0272bb2e7a8816ae103b2321648f011a52519499d3e"

        tools.get(download_url, sha256=sha)
        os.rename(release_name, SOURCE_SUBFOLDER)

    def build_requirements(self):
        installer = tools.SystemPackageTool()
        installer.install("autoconf-archive")

    def _configure_autotools(self, folder):
        cfg_args = ["--enable-bindings-cxx", "--enable-tools"]
        if self.options.shared:
            cfg_args += ["--enable-shared", "--disable-static"]
        else:
            cfg_args += ["--disable-shared", "--enable-static"]

        autotools = AutoToolsBuildEnvironment(self)

        # fixes error "undefined reference to `rpl_malloc'"
        env_vars = autotools.vars
        env_vars["ac_cv_func_malloc_0_nonnull"] = "yes"

        autotools.configure(configure_dir=folder, args=cfg_args, vars=env_vars)
        return autotools

    def build(self):
        source_folder = join(self.source_folder, SOURCE_SUBFOLDER)

        # autoreconf changes the content of the source folder, but for automatic build this
        # is fine as the source folder is copied into the build folder first
        self.run("autoreconf --force --install --verbose", cwd=source_folder)

        autotools = self._configure_autotools(source_folder)
        autotools.make()

    def package(self):
        source_folder = join(self.source_folder, SOURCE_SUBFOLDER)

        # Reconfigure to update the package folder
        autotools = self._configure_autotools(source_folder)
        autotools.install()

    def package_info(self):
        self.cpp_info.libs = ["gpiodcxx", "gpiod"]
