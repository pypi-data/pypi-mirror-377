# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from rer.blocks2html.testing import RER_BLOCKS2HTML_INTEGRATION_TESTING  # noqa: E501

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that rer.blocks2html is properly installed."""

    layer = RER_BLOCKS2HTML_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")

    def test_product_installed(self):
        """Test if rer.blocks2html is installed."""
        self.assertTrue(self.installer.is_product_installed("rer.blocks2html"))

    def test_browserlayer(self):
        """Test that IRerBlocks2HtmlLayer is registered."""
        from plone.browserlayer import utils
        from rer.blocks2html.interfaces import IRerBlocks2HtmlLayer

        self.assertIn(IRerBlocks2HtmlLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):
    layer = RER_BLOCKS2HTML_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstall_product("rer.blocks2html")
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if rer.blocks2html is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed("rer.blocks2html"))

    def test_browserlayer_removed(self):
        """Test that IRerBlocks2HtmlLayer is removed."""
        from plone.browserlayer import utils
        from rer.blocks2html.interfaces import IRerBlocks2HtmlLayer

        self.assertNotIn(IRerBlocks2HtmlLayer, utils.registered_layers())
