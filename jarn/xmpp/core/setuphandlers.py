from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from Products.ResourceRegistries.interfaces.settings import IResourceRegistriesSettings

def setupCMSUI(context):
    if context.readDataFile('cmsui.txt') is None:
        return
    registry = getUtility(IRegistry)
    rr_settings = registry.forInterface(IResourceRegistriesSettings)
    bundles = getattr(rr_settings, 'resourceBundlesForThemes', None)
    if bundles is None:
        return
    if 'cmsui' not in bundles:
        return
    bundles['cmsui'] = bundles['cmsui'] + ['xmpp']
