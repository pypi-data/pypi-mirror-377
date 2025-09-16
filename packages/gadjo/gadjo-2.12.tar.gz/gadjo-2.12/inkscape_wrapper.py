#! /usr/bin/env python3
# inkscape wrapper to support command-line parameters for <1.0 and 1.0
# versions.

import subprocess
import sys

inkscape_version = subprocess.check_output('inkscape --version', shell=True)
args = sys.argv[1:]
if b'Inkscape 0' not in inkscape_version:
    # --export-png replaced by --export-filename
    # --without-gui and --file removed
    args = [
        x.replace('--export-png', '--export-filename') for x in args if x not in ('--without-gui', '--file')
    ]

sys.exit(subprocess.call(['inkscape'] + args))
