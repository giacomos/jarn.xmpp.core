from plone.testing import z2
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting, FunctionalTesting
from twisted.words.protocols.jabber.jid import JID
from zope.component import getUtility
from zope.configuration import xmlconfig

from jarn.xmpp.twisted.testing import REACTOR_FIXTURE
from jarn.xmpp.twisted.testing import wait_on_deferred
from jarn.xmpp.twisted.testing import wait_for_client_state

from jarn.xmpp.core.interfaces import IAdminClient
from jarn.xmpp.core.subscribers.startup import setupAdminClient
from jarn.xmpp.core.utils.setup import setupXMPPEnvironment


class XMPPCoreFixture(PloneSandboxLayer):

    defaultBases = (REACTOR_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import jarn.xmpp.core
        import pas.plugins.userdeletedevent
        xmlconfig.file('configure.zcml', jarn.xmpp.core,
                       context=configurationContext)
        xmlconfig.file('configure.zcml', pas.plugins.userdeletedevent,
                       context=configurationContext)
        z2.installProduct(app, 'pas.plugins.userdeletedevent')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'jarn.xmpp.core:default')

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'pas.plugins.userdeletedevent')

    def testSetUp(self):
        setupAdminClient(None)
        client = getUtility(IAdminClient)
        wait_for_client_state(client, 'authenticated')
        d = setupXMPPEnvironment(client,
            member_jids=[JID('test_user_1_@localhost')],
            member_passwords={JID('test_user_1_@localhost'): 'secret'},
            content_nodes=[])
        wait_on_deferred(d)

    def testTearDown(self):
        client = getUtility(IAdminClient)
        client.disconnect()
        wait_for_client_state(client, 'disconnected')


XMPPCORE_FIXTURE = XMPPCoreFixture()

XMPPCORE_INTEGRATION_TESTING = IntegrationTesting(bases=(XMPPCORE_FIXTURE, ),
    name="XMPPCoreFixture:Integration")
XMPPCORE_FUNCTIONAL_TESTING = FunctionalTesting(bases=(XMPPCORE_FIXTURE, ),
    name="XMPPCoreFixture:Functional")