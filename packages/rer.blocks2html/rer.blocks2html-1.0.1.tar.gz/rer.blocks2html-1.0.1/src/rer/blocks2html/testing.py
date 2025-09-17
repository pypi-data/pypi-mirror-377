# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import rer.blocks2html


class RerBlocks2HtmlLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity

        self.loadZCML(package=plone.app.dexterity)
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=rer.blocks2html)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "rer.blocks2html:default")


RER_BLOCKS2HTML_FIXTURE = RerBlocks2HtmlLayer()


RER_BLOCKS2HTML_INTEGRATION_TESTING = IntegrationTesting(
    bases=(RER_BLOCKS2HTML_FIXTURE,),
    name="RerBlocks2HtmlLayer:IntegrationTesting",
)


RER_BLOCKS2HTML_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(RER_BLOCKS2HTML_FIXTURE,),
    name="RerBlocks2HtmlLayer:FunctionalTesting",
)


RER_BLOCKS2HTML_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        RER_BLOCKS2HTML_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="RerBlocks2HtmlLayer:AcceptanceTesting",
)
