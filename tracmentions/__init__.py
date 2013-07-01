#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright 2013-2018 Olemis Lang <olemis at gmail.com>
#
# License: BSD

r"""Trac 1.x plug-in that parses any ticket description or comment text with @<Username>.

When typing in @ a listing of existing users should appear at the cursors position
(basically like in Twitter) where you can either chose a user name from
or just continue typing. When a comment or description is saved, the
mentioned user should be automatically added to the ticket's CC field
(provide this as option to the plug-in). This will automatically lead
to the fact that the mentioned person will be notified and therefore
can react to the ticket's information flow.

The plug-in also parses 'hash tagged' words (like in Twitter or Google+)
Whenever user types a word with # e.g. #trac the word is linked and
the word is regarded as tag that is listed on a separate page. In order
to do so the plugin hooks into the existing #[ticket number] parser
without conflicts. Hence the ticket number parser remains working as
usual, but if a word starts after # it is regarded as regular tag.
When users click on the parsed hash tag, all connected tickets with
the same hash tag is listed. So this helps to semantically connect
tickets.

The source-code of the plug-in has been made open-source . It is
published on Nothing Agency GitHub account
(https://github.com/nothingagency) so others can either download the
source-code or contribute to it.

Copyright 2013-2018 Olemis Lang <olemis at gmail.com>
Licensed under the BSD License
"""
__author__ = 'Olemis Lang'

# Ignore errors to avoid Internal Server Errors
from trac.core import TracError
TracError.__str__ = lambda self: unicode(self).encode('ascii', 'ignore')

try:
    from tracmentions.web_ui import *
    msg = 'Ok'
except Exception, exc:
#    raise
    msg = "Exception %s raised: '%s'" % (exc.__class__.__name__, str(exc))
