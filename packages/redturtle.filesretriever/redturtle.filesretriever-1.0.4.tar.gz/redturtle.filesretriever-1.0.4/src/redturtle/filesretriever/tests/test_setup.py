# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles, TEST_USER_ID
from redturtle.filesretriever.testing import (
    REDTURTLE_FILESRETRIEVER_INTEGRATION_TESTING,  # noqa: E501,
)

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that redturtle.filesretriever is properly installed."""

    layer = REDTURTLE_FILESRETRIEVER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")

    def test_product_installed(self):
        """Test if redturtle.filesretriever is installed."""
        self.assertTrue(self.installer.isProductInstalled("redturtle.filesretriever"))

    def test_browserlayer(self):
        """Test that IRedturtleFilesretrieverLayer is registered."""
        from redturtle.filesretriever.interfaces import IRedturtleFilesretrieverLayer
        from plone.browserlayer import utils

        self.assertIn(IRedturtleFilesretrieverLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = REDTURTLE_FILESRETRIEVER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstallProducts(["redturtle.filesretriever"])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if redturtle.filesretriever is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled("redturtle.filesretriever"))

    def test_browserlayer_removed(self):
        """Test that IRedturtleFilesretrieverLayer is removed."""
        from redturtle.filesretriever.interfaces import IRedturtleFilesretrieverLayer
        from plone.browserlayer import utils

        self.assertNotIn(IRedturtleFilesretrieverLayer, utils.registered_layers())
