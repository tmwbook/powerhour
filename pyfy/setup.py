import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="py-fy",
    version="0.0.1",
    author="Tom White",
    author_email="twhite at wpi dot edu",
    description="A python wrapper for the Spotify API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="tbd",
    packages=setuptools.find_packages(),
    python_requires=">=3.6"
)
