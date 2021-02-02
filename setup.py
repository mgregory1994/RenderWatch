from setuptools import setup, find_packages

setup(
    name='Render Watch',
    version='0.1.0',
    packages=['startup', 'ffmpeg', 'encoding', 'app_handlers', 'app_formatting', 'render_watch_data'],
    package_dir={'': 'src'},
    py_modules=['main'],
    install_requires=[
        'PyGObject',
        'watchdog',
    ],
    package_data={
        'render_watch_data': ['*']
    },
    python_requires='>=3.8',
    url='https://github.com/mgregory1994/RenderWatch',
    license='GPLV3',
    author='Michael Gregory',
    author_email='michaelgregory@csus.edu',
    description='A professional video transcoder for Linux.'
)
