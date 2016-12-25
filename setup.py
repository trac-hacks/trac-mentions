#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from setuptools import setup

setup(
    name='TracMentionsPlugin',
    version='0.2.0',
    description="Notify users mentioned in comments",
    author='Olemis Lang',
    author_email='olemis+trac@gmail.com',
    maintainer='Olemis Lang',
    maintainer_email='olemis+trac@gmail.com',
    url='https://github.com/trac-hacks/trac-mentions',
    packages=['tracmentions'],
    package_data={
        'tracmentions': [
            'htdocs/*.js',
            'htdocs/*.css',
         ],
    },
    entry_points="""
        [trac.plugins]
        tracmentions = tracmentions.web_ui
        """,
    install_requires=['Trac'],
)
