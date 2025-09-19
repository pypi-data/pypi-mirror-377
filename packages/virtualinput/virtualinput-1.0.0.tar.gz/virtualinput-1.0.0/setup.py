from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="virtualinput",  # Unique name (virtualinput might be taken)
    version="1.0.0",
    author="off.rkv",
    author_email="off.rkv@gmail.com",
    description="Cross-platform virtual mouse and keyboard with ghost coordinates and Bézier curves",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/off-rkv/Virtual-Input",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)