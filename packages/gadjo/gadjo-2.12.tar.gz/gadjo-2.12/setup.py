#! /usr/bin/env python

import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

from setuptools import Command, find_packages, setup
from setuptools.command.build import build as _build
from setuptools.command.install_lib import install_lib as _install_lib
from setuptools.command.sdist import sdist
from setuptools.errors import CompileError

inkscape = os.path.abspath(os.path.join(os.path.dirname(__file__), 'inkscape_wrapper.py'))


class eo_sdist(sdist):
    def run(self):
        print('creating VERSION file')
        if os.path.exists('VERSION'):
            os.remove('VERSION')
        version = get_version()
        version_file = open('VERSION', 'w')
        version_file.write(version)
        version_file.close()
        sdist.run(self)
        print('removing VERSION file')
        if os.path.exists('VERSION'):
            os.remove('VERSION')


def get_version():
    '''Use the VERSION, if absent generates a version with git describe, if not
    tag exists, take 0.0- and add the length of the commit log.
    '''
    if os.path.exists('VERSION'):
        with open('VERSION') as v:
            return v.read()
    if os.path.exists('.git'):
        p = subprocess.Popen(
            ['git', 'describe', '--dirty=.dirty', '--match=v*'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        result = p.communicate()[0]
        if p.returncode == 0:
            result = result.decode('ascii').strip()[1:]  # strip spaces/newlines and initial v
            if '-' in result:  # not a tagged version
                real_number, commit_count, commit_hash = result.split('-', 2)
                version = '%s.post%s+%s' % (real_number, commit_count, commit_hash)
            else:
                version = result.replace('.dirty', '+dirty')
            return version
        else:
            return '0.0.post%s' % len(subprocess.check_output(['git', 'rev-list', 'HEAD']).splitlines())
    return '0.0'


class compile_translations(Command):
    description = 'compile message catalogs to MO files via django compilemessages'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        curdir = os.getcwd()
        try:
            from django.core.management import call_command

            for path, dirs, files in os.walk('gadjo'):
                if 'locale' not in dirs:
                    continue
                os.chdir(os.path.realpath(path))
                call_command('compilemessages')
                os.chdir(curdir)
        except ImportError:
            sys.stderr.write('!!! Please install Django >= 1.4 to build translations\n')
        finally:
            os.chdir(curdir)


class compile_scss(Command):
    description = 'compile scss files into css files'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        sass_bin = None
        for program in ('sassc', 'sass'):
            sass_bin = shutil.which(program)
            if sass_bin:
                break
        if not sass_bin:
            raise CompileError(
                'A sass compiler is required but none was found.  See sass-lang.com for choices.'
            )

        for package in self.distribution.packages:
            for package_path in __import__(package).__path__:
                for path, dirnames, filenames in os.walk(package_path):
                    for filename in filenames:
                        if not filename.endswith('.scss'):
                            continue
                        if filename.startswith('_'):
                            continue
                        subprocess.check_call(
                            [
                                sass_bin,
                                '%s/%s' % (path, filename),
                                '%s/%s' % (path, filename.replace('.scss', '.css')),
                            ],
                            env={'LC_ALL': 'C.UTF-8'},
                        )


class build_icons(Command):
    description = 'build icons'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        destpath = 'gadjo/static/css/icons/'
        if not os.path.exists(destpath):
            os.mkdir(destpath)
        variants_applications = {
            'small': {'colour': '386ede', 'width': '40'},
            'large': {'colour': 'e7e7e7', 'width': '80'},
            'large-hover': {'colour': 'bebebe', 'width': '80'},
        }
        variants_actions = {
            'small': {'colour': '386ede', 'width': '40'},
            'small.white': {'colour': 'ffffff', 'width': '40'},
            'hover': {'colour': '2b2b2b', 'width': '40'},
        }
        for basepath, dirnames, filenames in os.walk('icons'):
            for filename in filenames:
                basename = os.path.splitext(filename)[0]
                variants = variants_applications
                if not filename.endswith('.svg'):
                    continue
                if filename.startswith('action-'):
                    variants = variants_actions
                for variant in variants:
                    dest_filename = '%s.%s.png' % (basename, variant)
                    destname = os.path.join(destpath, dest_filename)
                    self.generate(os.path.join(basepath, filename), destname, **variants.get(variant))

    def generate(self, src, dest, colour, width, **kwargs):
        if os.path.exists(dest) and os.stat(dest).st_mtime >= os.stat(src).st_mtime:
            return
        # default values
        from PIL import Image, PngImagePlugin

        license = 'Creative Commons Attribution-Share Alike 3.0'
        if 'old-set' in src:
            author = 'GNOME Project'
            tree = ET.fromstring(open(src).read().replace('#000000', '#%s' % colour))
            for elem in tree.findall('*'):
                if not elem.attrib.get('style'):
                    elem.attrib['style'] = 'fill:#%s' % colour
        else:
            author = "J'articule"
            tree = ET.fromstring(open(src).read())
            for elem in tree.findall('{http://www.w3.org/2000/svg}defs/{http://www.w3.org/2000/svg}style'):
                elem.text = elem.text.replace('242d3c', colour)

        f = tempfile.NamedTemporaryFile(suffix='.svg', delete=False)
        f.write(ET.tostring(tree))
        f.close()

        subprocess.call(
            [
                inkscape,
                '--without-gui',
                '--file',
                f.name,
                '--export-area-drawing',
                '--export-area-snap',
                '--export-png',
                dest,
                '--export-width',
                width,
            ]
        )

        # write down licensing info in the png file
        meta = PngImagePlugin.PngInfo()
        meta.add_text('Licence', license, 0)
        png_file = Image.open(dest)
        png_file.save(dest, 'PNG', pnginfo=meta)


class build(_build):
    sub_commands = [
        ('compile_translations', None),
        ('compile_scss', None),
        ('build_icons', None),
    ] + _build.sub_commands


class install_lib(_install_lib):
    def run(self):
        self.run_command('compile_translations')
        _install_lib.run(self)


setup(
    name='gadjo',
    version=get_version(),
    license='AGPLv3 or later',
    description='Django base template tailored for management interfaces',
    url='https://dev.entrouvert.org/projects/gadjo/',
    author='Frederic Peters',
    author_email='fpeters@entrouvert.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'XStatic>=1.0.3',
        'XStatic_Font_Awesome<5',
        'XStatic_jQuery',
        'XStatic_jquery_ui',
        'XStatic_OpenSans',
    ],
    setup_requires=[
        'Pillow',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    zip_safe=False,
    cmdclass={
        'build': build,
        'build_icons': build_icons,
        'compile_scss': compile_scss,
        'compile_translations': compile_translations,
        'install_lib': install_lib,
        'sdist': eo_sdist,
    },
)
