import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SM2ST",
    version="0.0.1",
    author="LLX",
    author_email="llx_1910@163.com",
    description="SM2ST: Automatic registration of spatial metabolome and spatial transcriptome via adversarial autoencoders",  # 包的简述
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/binbin-coder/SM2ST",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)