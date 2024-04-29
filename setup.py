from setuptools import setup, find_packages

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

with open("requirements-dev.txt", "r", encoding="utf-8") as fh:
    requirements_dev = fh.read()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="uqload_dl_gui",
    version="1.0",
    author="Joel Flores",
    author_email="joelhernandez2982@gmail.com",
    license="GPLv3",
    description="A simple video downloader",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        "test": requirements_dev,
    },
    python_requires=">=3.9",
    project_urls={
        "Issue Tracker": "https://github.com/JoelFH23/uqload-downloader-gui/issues",
        "Source Code": "https://github.com/JoelFH23/uqload-downloader-gui",
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    entry_points={
        "console_scripts": [
            "uqload-dl-gui=uqload_dl_gui.main:main",
        ]
    },
)
