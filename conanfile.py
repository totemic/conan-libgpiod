from conans import ConanFile, AutoToolsBuildEnvironment, tools


class LibgpiodConan(ConanFile):
    name = "libgpiod"
    version = "1.2"
    license = "LGPL-2.1-or-later"
    author = "Michael Beach <michaelb@ieee.org>"
    url = "https://github.com/mbeach/conan-libgpiod"
    description = "Library for interacting with the linux GPIO character device"
    topics = ("gpio")
    exports_sources = "chip_iter.patch"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def system_requirements(self):
        installer = tools.SystemPackageTool()
        installer.install("autoconf-archive")

    def source(self):
        git = tools.Git(folder="libgpiod")
        git.clone("https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git", "v" + self.version)
        tools.patch(patch_file="chip_iter.patch", base_path="libgpiod")

    def build(self):
        self.run("autoreconf --force --install --verbose", cwd="libgpiod")
        cfgArgs = ["--enable-bindings-cxx"]
        if self.options.shared:
            cfgArgs += ["--enable-shared", "--disable-static"]
        else:
            cfgArgs += ["--disable-shared", "--enable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        envVars = autotools.vars
        envVars["ac_cv_func_malloc_0_nonnull"] = "yes"
        autotools.configure(
            configure_dir="libgpiod",
            args=cfgArgs,
            vars=envVars)
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING", src="libgpiod", keep_path=False)
        self.copy("*.h", dst="include", src="libgpiod/include")
        self.copy("*.hpp", dst="include", src="libgpiod/bindings/cxx")
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["gpiodcxx", "gpiod"]
