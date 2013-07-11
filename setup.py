try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='pydeely',
    packages=['pydeely'],
    version='0.0.1',
    description='Feedly API for Python',
    license='MIT License',
    author='Sunguk Lee',
    author_email='d3m3vilurr@gmail.com',
    install_requires=['requests', 'html2text'],
    tests_require=['pytest', 'pytest-cov'],
    extras_require={'doc': ['Sphinx']},
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
