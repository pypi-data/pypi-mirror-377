import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="streamlit-custom-checkbox-rpathak",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A custom checkbox component for Streamlit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rpathak/streamlit-custom-checkbox-rpathak",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "streamlit >= 0.63",
    ],
)