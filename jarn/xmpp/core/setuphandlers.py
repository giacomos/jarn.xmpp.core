from zope.component import getUtility


def setupCMSUI(context):
    if context.readDataFile('cmsui.txt') is None:
        return
    portal = context.getSite()
