import os, sys
import setuptools

descx = '''PyEdPro is modern multi-platform editor. Simple, powerful,
configurable, extendable. Goodies like macro recording / playback, spell check,
column select, multiple clipboards, unlimited persistent undo ...
   PyEdPro.py has macro recording/play, search/replace, one click function navigation,
auto backup, undo/redo, auto complete, auto correct, syntax check, spell suggestion
 ... and a lot more.
   The recorded macros, the undo / redo information the editing session details persist
 after the editor is closed.
    The spell checker can check code comments. The parsing of the code is
rudimentary, comments and strings are spell checked. (Press F9 or Shit-F9) The code is filtered
out for Python and  'C'. The spell checker is executed on live text. (while typing)
'''

classx = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        ]

includex = [ "*", ]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
#os.remove("README.copy.md")

# Get version number from the main file:
fp = open("testvdrive.py", "rt")
vvv = fp.read(); fp.close()
loc_vers =  '1.0.0'     # Default
for aa in vvv.split("\n"):
    idx = aa.find("VERSION ")
    if idx == 0:        # At the beginning of line
        try:
            loc_vers = aa.split()[2].replace('"', "")
            break
        except:
            pass
#print("loc_vers:", loc_vers)
#sys.exit()

deplist = []

setuptools.setup(
    name="testvdrive",
    version=loc_vers,
    author="Peter Glen",
    author_email="peterglen99@gmail.com",
    description="Python test by send / expect.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    #url="https://github.com/pglen/pyedpro",
    classifiers=classx,
    include_package_data=True,
    packages=setuptools.find_packages(include=includex),
    scripts = ['testvdrive.py', ],

    package_dir = { },

    package_data= { },

    data_files = [ ],

    python_requires='>=3',
    install_requires=deplist,
    entry_points={
        'console_scripts': [
            "testvdrive=testvdrive:mainfunct",
            ],
    },
)

# EOF