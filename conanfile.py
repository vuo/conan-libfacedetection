from conans import ConanFile, CMake, tools
import os
import platform
import shutil

class LibfacedetectionConan(ConanFile):
    name = 'libfacedetection'

    # libfacedetection has no tagged releases, so just use package_version.
    source_version = '1'
    package_version = '1'
    version = '%s-%s' % (source_version, package_version)

    build_requires = (
        'llvm/5.0.2-1@vuo/stable',
        'macos-sdk/11.0-0@vuo/stable',
    )
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://github.com/ShiqiYu/libfacedetection'
    license = 'https://github.com/ShiqiYu/libfacedetection/blob/master/LICENSE'
    description = 'A library for face detection in images'
    source_dir = 'libfacedetection'

    build_x86_dir = '_build_x86'
    build_x86avx2_dir = '_build_x86avx2'
    build_arm_dir = '_build_arm'
    install_x86_dir = '_install_x86'
    install_x86avx2_dir = '_install_x86avx2'
    install_arm_dir = '_install_arm'

    generators = 'cmake'

    def source(self):
        self.run("git clone https://github.com/ShiqiYu/libfacedetection.git")
        with tools.chdir(self.source_dir):
            self.run("git checkout 1ed30e7")

        self.run('mv %s/LICENSE %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        cmake = CMake(self)

        cmake.definitions['CMAKE_BUILD_TYPE'] = 'Release'
        cmake.definitions['BUILD_SHARED_LIBS'] = 'ON'
        cmake.definitions['CMAKE_CXX_COMPILER'] = self.deps_cpp_info['llvm'].rootpath + '/bin/clang++'
        cmake.definitions['CMAKE_C_COMPILER']   = self.deps_cpp_info['llvm'].rootpath + '/bin/clang'
        cmake.definitions['CMAKE_C_FLAGS'] = cmake.definitions['CMAKE_CXX_FLAGS'] = '-Oz -DNDEBUG'
        cmake.definitions['CMAKE_CXX_FLAGS'] += ' -stdlib=libc++'
        cmake.definitions['CMAKE_OSX_DEPLOYMENT_TARGET'] = '10.11'
        cmake.definitions['CMAKE_OSX_SYSROOT'] = self.deps_cpp_info['macos-sdk'].rootpath

        cmake.definitions['CMAKE_INSTALL_NAME_DIR'] = '@rpath'
        cmake.definitions['CMAKE_BUILD_WITH_INSTALL_NAME_DIR'] = 'ON'

        self.output.info("=== Build for x86_64 ===")
        cmake.definitions['CMAKE_INSTALL_PREFIX'] = '%s/%s' % (os.getcwd(), self.install_x86_dir)
        cmake.definitions['CMAKE_OSX_ARCHITECTURES'] = 'x86_64'
        tools.mkdir(self.build_x86_dir)
        with tools.chdir(self.build_x86_dir):
            cmake.definitions['ENABLE_AVX2'] = 'OFF'
            cmake.definitions['ENABLE_AVX512'] = 'OFF'
            cmake.definitions['ENABLE_NEON'] = 'OFF'
            cmake.configure(source_dir='../%s' % self.source_dir, build_dir='.')
            cmake.build()
            cmake.install()

        self.output.info("=== Build for x86_64-avx2 ===")
        cmake.definitions['CMAKE_INSTALL_PREFIX'] = '%s/%s' % (os.getcwd(), self.install_x86avx2_dir)
        tools.mkdir(self.build_x86avx2_dir)
        with tools.chdir(self.build_x86avx2_dir):
            cmake.definitions['CMAKE_OSX_ARCHITECTURES'] = 'x86_64'
            cmake.definitions['ENABLE_AVX2'] = 'ON'
            cmake.definitions['ENABLE_AVX512'] = 'OFF'
            cmake.definitions['ENABLE_NEON'] = 'OFF'
            cmake.configure(source_dir='../%s' % self.source_dir, build_dir='.')
            cmake.build()
            cmake.install()

        self.output.info("=== Build for arm64 ===")
        cmake.definitions['CMAKE_INSTALL_PREFIX'] = '%s/%s' % (os.getcwd(), self.install_arm_dir)
        tools.mkdir(self.build_arm_dir)
        with tools.chdir(self.build_arm_dir):
            cmake.definitions['CMAKE_OSX_ARCHITECTURES'] = 'arm64'
            cmake.definitions['ENABLE_AVX2'] = 'OFF'
            cmake.definitions['ENABLE_AVX512'] = 'OFF'
            cmake.definitions['ENABLE_NEON'] = 'ON'
            cmake.configure(source_dir='../%s' % self.source_dir, build_dir='.')
            cmake.build()
            cmake.install()

    def package(self):
        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'
        else:
            raise Exception('Unknown platform "%s"' % platform.system())

        self.copy('*.h', src='%s/include/facedetection' % self.install_x86_dir, dst='include')

        with tools.chdir('%s/lib' % self.install_x86_dir):
            shutil.move('libfacedetection.%s' % libext, 'libfacedetection_x86.%s' % libext)
            self.run('install_name_tool -id @rpath/libfacedetection_x86.dylib libfacedetection_x86.dylib')
        self.copy('libfacedetection_x86.%s' % libext, src='%s/lib' % self.install_x86_dir, dst='lib')

        with tools.chdir('%s/lib' % self.install_x86avx2_dir):
            shutil.move('libfacedetection.%s' % libext, 'libfacedetection_x86avx2.%s' % libext)
            self.run('install_name_tool -id @rpath/libfacedetection_x86avx2.dylib libfacedetection_x86avx2.dylib')
        self.copy('libfacedetection_x86avx2.%s' % libext, src='%s/lib' % self.install_x86avx2_dir, dst='lib')

        with tools.chdir('%s/lib' % self.install_arm_dir):
            shutil.move('libfacedetection.%s' % libext, 'libfacedetection_arm.%s' % libext)
            self.run('install_name_tool -id @rpath/libfacedetection_arm.dylib libfacedetection_arm.dylib')
        self.copy('libfacedetection_arm.%s' % libext, src='%s/lib' % self.install_arm_dir, dst='lib')

        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        # Don't set self.cpp_info.libs, since the client needs to decide which of the 2 libraries to use.
        self.cpp_info.includedirs = ['include']
