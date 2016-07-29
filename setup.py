from   os.path    import dirname, join
import re
from   setuptools import setup

with open(join(dirname(__file__), 'daemail', '__init__.py')) as fp:
    for line in fp:
        m = re.search(r'^\s*__version__\s*=\s*([\'"])([^\'"]+)\1\s*$', line)
        if m:
            version = m.group(2)
            break
    else:
        raise RuntimeError('Unable to find own __version__ string')

with open(join(dirname(__file__), 'README.rst')) as fp:
    long_desc = fp.read()

setup(
    name='daemail',
    version=version,
    packages=['daemail'],
    license='MIT',
    author='John Thorvald Wodder II',
    author_email='daemail@varonathe.org',
    ###keywords='',
    description='Daemonize a command and e-mail the results',
    long_description=long_desc,
    url='https://github.com/jwodder/daemail',

    install_requires=['python-daemon'],

    classifiers=[
        'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',

        'License :: OSI Approved :: MIT License',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Topic :: Communications :: Email',
        'Topic :: Utilities',
    ],

    entry_points={
        "console_scripts": [
            'daemail = daemail.__main__:main',
        ]
    },
)