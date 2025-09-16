from setuptools import setup, dist
from setuptools.extension import Extension
from os import path
import os
from codecs import open
from setuptools.command.install import install
from distutils.spawn import find_executable

dir_path = path.dirname(path.realpath(__file__))

include_dirs = [dir_path + "/PyRuSH", dir_path]





here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.MD'), encoding='utf-8') as f:
    long_description = f.read()

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        import subprocess
        import sys
        try:
            # Check if java is installed and is JDK 8
            result = subprocess.run(['java', '-version'], capture_output=True, text=True)
            version_output = result.stderr if result.stderr else result.stdout
            if 'version "1.8' in version_output or 'version "8' in version_output:
                print("JDK 8 is already installed.")
                return
            else:
                print("Java is installed but not JDK 8. Installing JDK 8...")
        except Exception:
            print("Java is not installed. Installing JDK 8...")
        try:
            import jdk
        except ImportError:
            print("install-jdk not found, installing it...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'install-jdk'])
            import jdk
        print("Installing JDK 8 using install-jdk...")
        jdk.install('8')
        print("JDK 8 installation complete.")




def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line.split("#")[0].strip() for line in lineiter if line and not line.startswith("#")]

print(parse_requirements('requirements.txt'))

def get_version():
    """Load the version from VERSION, without importing it.

    This function assumes that the last line in the file contains a variable defining the
    version string with single quotes.

    """
    try:
        return open(os.path.join(os.path.dirname(__file__), 'PyRuSH', 'VERSION')).read()
    except IOError:
        return "0.0.0a1"

COMPILER_DIRECTIVES = {
    "language_level": 3,
    "embedsignature": True,
    "annotation_typing": False,
}



setup(
    name='py4jrush',
    packages=['py4jrush'],  # this must be the same as the name above
    version=get_version(),
    description='A fast implementation of RuSH (Rule-based sentence Segmenter using Hashing).',
    author='Jianlin',
    author_email='jianlinshi.cn@gmail.com',
    url='https://github.com/jianlins/py4jrush',  # update to new repo URL
    keywords=['sentence segmentation', 'sentence splitting'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    package_data={
        'py4jrush': ['lib/*.jar'],
    },
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Development Status :: 3 - Alpha',
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    license='Apache License',
    zip_safe=False,
    install_requires=parse_requirements('requirements.txt'),
    tests_require='pytest',
    cmdclass={
        'install': PostInstallCommand,
    }
            # url parameter already set above, remove duplicate
)
