#!/usr/bin/env python3

from setuptools import setup


setup(
    name='Render Watch',
    version='0.3.0',
    url='https://github.com/mgregory1994/RenderWatch',
    license='GPLV3',
    author='Michael Gregory',
    author_email='michaelgregoryn@gmail.com',
    description='A professional video transcoder for Linux.',
    python_requires='~=3.9',
    package_dir={'': 'src'},
    packages=[
        'render_watch', 'render_watch/ffmpeg'
    ],
    install_requires=[
        'watchdog'
    ],
    data_files=[
        ('share/applications', ['data/render-watch.desktop']),
        ('share/icons/hicolor/64x64/apps', ['data/icons/hicolor/64x64/apps/RenderWatch.png']),
        ('share/icons/hicolor/128x128/apps', ['data/icons/hicolor/128x128/apps/RenderWatch.png']),
        ('share/icons/hicolor/512x512/apps', ['data/icons/hicolor/512x512/apps/RenderWatch.png'])
    ],
    scripts=[
        'scripts/render-watch',
        'scripts/render-watch-debug'
    ]
)
