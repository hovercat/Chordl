import setuptools
import py2exe

setuptools.setup(
    name="chordlsync",
    version="0.2",
    author="Aschl Ulrich, Gnaore Kanon",
    author_email="dont.at@me.com",
    description="Sync Tool",
    url="https://github.com/hovercat/Chordl",
	packages=['sound_synchronization'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
	install_requires=[
		'numpy',
		'scipy',
		'matplotlib',
		'pandas',
		'soundfile',
		'sklearn'
	],
	entry_points={
         'console_scripts': ['chordl=sound_synchronization.chordlsync:main'],
     },
	console=['chordlsync'],
)