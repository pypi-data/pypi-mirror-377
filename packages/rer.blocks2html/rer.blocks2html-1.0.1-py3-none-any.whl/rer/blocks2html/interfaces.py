# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from zope.interface import Interface


class IBlocksToHtml(Interface):
    """
    Utility that converts blocks to html
    """
