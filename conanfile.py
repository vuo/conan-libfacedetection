from conans import ConanFile, CMake, tools
import platform

class LibfacedetectionConan(ConanFile):
    name = 'libfacedetection'

    # libfacedetection has no tagged releases, so just use package_version.
    source_version = '0'
    package_version = '0'
    version = '%s-%s' % (source_version, package_version)

    build_requires = 'llvm/3.3-5@vuo/stable'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://github.com/ShiqiYu/libfacedetection'
    license = 'https://github.com/ShiqiYu/libfacedetection/blob/master/LICENSE'
    description = 'A library for face detection in images'
    source_dir = 'libfacedetection'
    build_dir = '_build'
    generators = 'cmake'

    def source(self):
        self.run("git clone https://github.com/ShiqiYu/libfacedetection.git")
        with tools.chdir(self.source_dir):
            self.run("git checkout b059dfa")

        self.run('mv %s/LICENSE %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            cmake = CMake(self)

            cmake.definitions['CMAKE_BUILD_TYPE'] = 'Release'
            cmake.definitions['CMAKE_CXX_COMPILER'] = self.deps_cpp_info['llvm'].rootpath + '/bin/clang++'
            cmake.definitions['CMAKE_C_COMPILER']   = self.deps_cpp_info['llvm'].rootpath + '/bin/clang'
            cmake.definitions['CMAKE_C_FLAGS'] = cmake.definitions['CMAKE_CXX_FLAGS'] = '-Oz -DNDEBUG'
            cmake.definitions['CMAKE_CXX_FLAGS'] += ' -stdlib=libc++ -I' + ' -I'.join(self.deps_cpp_info['llvm'].include_paths)
            cmake.definitions['CMAKE_OSX_ARCHITECTURES'] = 'x86_64'
            cmake.definitions['CMAKE_OSX_DEPLOYMENT_TARGET'] = '10.10'
            cmake.definitions['CMAKE_INSTALL_NAME_DIR'] = '@rpath'
            cmake.definitions['CMAKE_BUILD_WITH_INSTALL_NAME_DIR'] = 'ON'
            cmake.definitions['ENABLE_AVX2'] = 'ON'

            cmake.configure(source_dir='../%s' % self.source_dir,
                            build_dir='.')
            cmake.build()

    def package(self):
        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'
        else:
            raise Exception('Unknown platform "%s"' % platform.system())

        self.copy('*.h', src='%s/src' % self.source_dir, dst='include')
        self.copy('libfacedetection.%s' % libext, src='%s' % self.build_dir, dst='lib')

        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        self.cpp_info.libs = ['facedetection']
        self.cpp_info.includedirs = ['include']
