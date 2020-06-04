import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="spotckup",
    version="0.1.1",
    author="mattiaforc",
    author_email="mattiaforc@gmail.com",
    description="A small utility for creating JSON local backups of music and playlists from spotify",
    long_description=long_description,
    url="https://github.com/mattiaforc/spotckup",
    keywords="spotify backup utility json store",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'Click',
        'requests',
        'certifi',
        'idna',
        'urllib3'
    ],
    entry_points={
        'console_scripts': [
            'spotckup=spotckup.cli:spotckup',  # command=package.module:function
        ],
    },

)
