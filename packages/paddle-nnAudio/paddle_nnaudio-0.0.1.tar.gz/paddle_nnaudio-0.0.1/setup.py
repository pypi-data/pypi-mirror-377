import setuptools
import codecs
import os.path

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setuptools.setup(
    name="paddle_nnAudio",
    version=get_version("ppAudio/__init__.py"),
    author="PlumBlossom",
    author_email="1589524335@qq.com",
    description="A fast GPU audio processing toolbox with 1D convolutional neural network",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PlumBlossomMaid/ppAudio",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "scipy>=1.2.0",
        "numpy>=1.14.5",
        #"paddlepaddle>=2.0.0",
    ],
    extras_require={"tests": ["pytest", "librosa"]},
)
