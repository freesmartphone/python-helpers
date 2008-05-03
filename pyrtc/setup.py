from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
setup(
  name = "PyRTC",
  version = "1.0.0",
  author = "Michael 'Mickey' Lauer",
  email = "mlauer@vanille-media.de",
  ext_modules=[ 
    Extension("pyrtc", ["pyrtc.pyx"], libraries = [])
    ],
  cmdclass = {'build_ext': build_ext}
)
