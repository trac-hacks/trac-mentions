# -*- coding: utf-8 -*-
#

import re

from trac.config import Option
from trac.core import Component, implements
from trac.web.api import IRequestFilter
from trac.web.chrome import Chrome, ITemplateProvider, add_script, \
                            add_script_data, add_stylesheet
from trac.web.href import Href


class MentionsModule(Component):
    """Autocomplete @<Username> or #<tag>. Parse any ticket description or
    comment text to leverage hashtags as Trac tags
    """
    implements(IRequestFilter, ITemplateProvider)

    underscore_location = Option('trac', 'underscorejs_location',
        'https://cdnjs.cloudflare.com/ajax/libs/underscore.js/1.8.3/',
        doc="""Path to underscore.js library""")

    @property
    def underscore_href(self):
        return Href(self.underscore_location)

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        from pkg_resources import resource_filename
        return [('mentions', resource_filename('tracmentions', 'htdocs'))]

    def get_templates_dirs(self):
        return []

    # IRequestFilter Methods

    def pre_process_request(self, req, handler):
        # Read the fields that support wiki formatting
        comment = req.args.get('comment')
        description = req.args.get('field_description')
        if comment or description:
            # Parse the wiki-formatted fields to get the mentioned users
            comment_users = description_users = []
            if comment:
                comment_users = re.findall('(?<=@)[\w]+', comment)
            if description:
                description_users = re.findall('(?<=@)[\w]+', description)
            mentioned_users = set(comment_users) | set(description_users)

            # Create the value for field_cc
            field_cc = req.args.get('field_cc')
            for user in mentioned_users:
                # Add the user to CC: if it is not already there
                if not re.findall('^' + user + '(?=[\s,]|$)|(?<=[\s,])' +
                                          user + '(?=[\s,]|$)', field_cc):
                    # Add a ',' if there are already some users in the field
                    if field_cc:
                        field_cc += ', '
                    field_cc += user
            req.args['field_cc'] = field_cc

        return handler

    def post_process_request(self, req, template, data, content_type):
        if template == 'ticket.html':
            users = [{
                'id': (username or ''),
                'value': '@' + (username or ''),
                'name': (name or '') + ' (' + (username or '') + ')',
                'avatar': '/contacts/' + (username or '') + '.gif',
                'type': 'contact'
            } for username, name, email in self.env.get_known_users()]
            add_script_data(req, {'UserList': users})

            if self.underscore_location:
                add_script(req, self.underscore_href('underscore-min.js'))
                add_script(req, 'mentions/jquery.mentionsInput.js')
                add_stylesheet(req, 'mentions/jquery.mentionsInput.css')
                add_script(req, 'mentions/mentions.js')
            else:
                self.log.warning("MentionsModule can't work because of "
                                 "missing configuration")

            # Read the fields that support wiki formatting
            comment = req.args.get('comment')
            description = req.args.get('field_description')
            if comment or description:
                # Parse the wiki-formatted fields to get the mentioned users
                comment_users = re.findall('(?<=@)[\w]+', comment)
                description_users = re.findall('(?<=@)[\w]+', description)
                mentioned_users = set(comment_users) | set(description_users)

                chrome = Chrome(self.env)
                field_cc = req.args.get('field_cc')
                cc_list = set(chrome.cc_list(field_cc))
                cc_list.update(mentioned_users)
                field_cc = ', '.join(sorted(cc_list))

                ticket = data['ticket']
                old_cc_list = chrome.cc_list(ticket._old.get('cc', []))
                old_field_cc = ', '.join(sorted(old_cc_list))

                # Add the created field_cc value to data dict
                if field_cc != req.args.get('field_cc'):
                    new_cc = {
                        'new': field_cc,
                        'old': old_field_cc,
                        'by': req.authname,
                        'label': 'Cc'
                    }

                    if data.get('change_preview'):
                        data['change_preview']['fields'].update({
                            'cc': new_cc
                        })

                    if data.get('description change'):
                        data['description change']['fields'].update({
                            'cc': new_cc
                        })

        return template, data, content_type
