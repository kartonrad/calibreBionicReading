#!/usr/bin/env python
# vim:fileencoding=utf-8


__license__ = 'FEMBOY ASS'
__copyright__ = '2022, Bingus <bingusBruh>'

from calibre.customize import EditBookToolPlugin


class DemoPlugin(EditBookToolPlugin):

    name = 'Bionic-Reading, Edit Plugin'
    version = (1, 1, 0)
    author = 'Bingus'
    supported_platforms = ['windows', 'osx', 'linux']
    description = 'Boldens the start of every word, to create fixation points, to ease reading? Its black magic.'
    minimum_calibre_version = (1, 46, 0)
