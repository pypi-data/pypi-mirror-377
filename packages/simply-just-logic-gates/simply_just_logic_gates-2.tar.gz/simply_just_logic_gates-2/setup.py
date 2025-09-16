from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).parent

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name='simply_just_logic_gates',
    packages=['lg'],
    version='2',
    author='Error Dev',
    author_email='3rr0r.d3v@gmail.com',
    description='Simply Just Logic Gates',
    python_requires='>=3.6',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python',
        'Environment :: Console',
        'Framework :: IDLE',
        'Natural Language :: English',
    ],
)