from conans import ConanFile, CMake
import platform

class LibfacedetectonTestConan(ConanFile):
    build_requires = 'llvm/3.3-5@vuo/stable'
    generators = 'cmake'

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy('*', src='lib', dst='lib')

    def test(self):
        if platform.system() == 'Darwin':
            self.run('./bin/test_package 2>&1 | fgrep -v "data is null."')

        # Ensure we only link to system libraries and our own libraries.
        if platform.system() == 'Darwin':
            self.run('! (otool -L lib/libfacedetection.dylib | grep -v "^lib/" | egrep -v "^\s*(/usr/lib/|/System/|@rpath/)")')
            self.run('! (otool -L lib/libfacedetection.dylib | fgrep "libstdc++")')
            self.run('! (otool -l lib/libfacedetection.dylib | grep -A2 LC_RPATH | cut -d"(" -f1 | grep "\s*path" | egrep -v "^\s*path @(executable|loader)_path")')
        elif platform.system() == 'Linux':
            self.run('! (ldd lib/libfacedetection.so | grep -v "^lib/" | grep "/" | egrep -v "(\s(/lib64/|(/usr)?/lib/x86_64-linux-gnu/)|test_package/build)")')
            self.run('! (ldd lib/libfacedetection.so | fgrep "libstdc++")')
        else:
            raise Exception('Unknown platform "%s"' % platform.system())
