#!/usr/bin/env python3

from setuptools import setup


setup(
    name='Render Watch',
    version='0.1.1',
    url='https://github.com/mgregory1994/RenderWatch',
    license='GPLV3',
    author='Michael Gregory',
    author_email='michaelgregoryn@gmail.com',
    description='A professional video transcoder for Linux.',
    python_requires='~=3.8',
    package_dir={'': 'src'},
    packages=[
        'render_watch', 'render_watch/app_formatting', 'render_watch/app_handlers', 'render_watch/encoding',
        'render_watch/ffmpeg', 'render_watch/helpers', 'render_watch/render_watch_data', 'render_watch/signals',
        'render_watch/signals/aac', 'render_watch/signals/active_page', 'render_watch/signals/active_row',
        'render_watch/signals/completed_page', 'render_watch/signals/completed_row', 'render_watch/signals/crop',
        'render_watch/signals/inputs_page', 'render_watch/signals/inputs_row', 'render_watch/signals/main_window',
        'render_watch/signals/nvenc', 'render_watch/signals/opus', 'render_watch/signals/prefs',
        'render_watch/signals/preview', 'render_watch/signals/settings_sidebar', 'render_watch/signals/trim',
        'render_watch/signals/vp9', 'render_watch/signals/x264', 'render_watch/signals/x265', 'render_watch/startup'
    ],
    install_requires=[
        'PyGObject',
        'watchdog',
    ],
    package_data={
        'render_watch/render_watch_data': ['*']
    },
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
