import re
import json
import urllib2
from urlparse import urlparse

from BeautifulSoup import BeautifulSoup

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView


class MagicLinksView(BrowserView):

    def __call__(self, url):
        try:
            doc = urllib2.urlopen(url).read()
        except urllib2.URLError:
            return None
        doc = BeautifulSoup(urllib2.urlopen(url).read())
        title = u''
        description = u''

        # title
        if doc.title:
            title = doc.title.string
        if not title:
            title = doc.first('meta', attrs={'name': 'title'})
            if title:
                title = title.get('content')

        # description
        description = doc.first('meta', attrs={'name': 'description'})
        if description:
            description = description.get('content')

        # Find favicon
        favicon_url = doc.first('link', rel='shortcut icon')
        if favicon_url:
            favicon_url = favicon_url.get('href')
        else:
            host_url = urlparse(url)
            favicon_url = host_url[0] + u'://' + host_url[1] + u'/favicon.ico'

        return json.dumps({
            'title': title,
            'description': description,
            'favicon_url': favicon_url})


class ContentTransform(BrowserView):

    def __call__(self, text):
        tr = getToolByName(self.context, 'portal_transforms')
        text = tr.convert('web_intelligent_plain_text_to_html', text).getData()
        user_pattern = re.compile(r'@[\w\.\-@]+')
        user_refs = user_pattern.findall(text)
        mt = getToolByName(self.context, 'portal_membership')
        portal_url = getToolByName(self.context, 'portal_url')()
        for user_ref in user_refs:
            user_id = user_ref[1:]
            if mt.getMemberById(user_id) is not None:
                link = '<a href="%s/pubsub-feed?node=%s">%s</a>' % \
                    (portal_url, user_id, user_ref)
                text = user_pattern.sub(link, text)
        result = {'text': text}
        return json.dumps(result)