#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright 2013-2018 Olemis Lang <olemis at gmail.com>
#
# License: BSD

r"""Parse any ticket description or comment text with @<Username> or #<tag>.

Copyright 2013-2018 Olemis Lang <olemis at gmail.com>
Licensed under the BSD License
"""
__author__ = 'Olemis Lang'

import pkg_resources

from genshi.core import START
from genshi.filters.transform import Transformer

from trac.config import Option
from trac.core import Component, implements
from trac.web.api import ITemplateStreamFilter
from trac.web.chrome import add_script, add_stylesheet, ITemplateProvider, add_script_data
from trac.web.href import Href
from trac.web import IRequestFilter
from trac.web.chrome import Chrome
import re

class MentionsModule(Component):
    """Autocomplete @<Username> or #<tag>. Parse any ticket description or
    comment text to leverage hashtags as Trac tags
    """
    implements(ITemplateProvider, ITemplateStreamFilter, IRequestFilter)

    jquery_mentions_location = Option('trac', 'jquery_mentions_location', 
                                      doc="""Path to jquery mentions plugin""")

    underscore_location = Option('trac', 'underscorejs_location', 
                                 doc="""Path to underscore.js library""")

    @property
    def underscore_href(self):
        return Href(self.underscore_location)

    # ITemplateProvider methods                                             
    def get_htdocs_dirs(self):                                              
        return [('mentions',                                                
             pkg_resources.resource_filename('tracmentions', 'htdocs'))]

    def get_templates_dirs(self):                                           
        return []                                                           


    # ITemplateStreamFilter methods

    def filter_stream(self, req, method, filename, stream, data):
        """Setup user and tags autocompletion"""

        if method == 'xhtml':
            return self._process_stream(req, stream)
        return stream

    # Protected methods

    def _process_stream(self, req, stream):
        """Filter stream to install user / hashtag autocompletion if any
        of the follwing is found

          - textarea.wikitext
          - .ticket input#field-owner , .ticket input#field-reporter (users)
        """
        # Pre-process stream to match known targets
        stream = stream | Transformer('//textarea[contains(@class, "wikitext")]') \
                          .attr('data-trac-mentions', 'all').end() \

        #Add the users data to page
        i = 0
        Users = []
        for i, (username, name, email) in enumerate(self.env.get_known_users()):
            #self.log.warning("%s \t %s \t %s\n", username, name, email)
            UserObject = dict({'id': (username or ''),
                          'value' : '@' + (username or ''),
                          'name': (name or '') + " (" + (username or '') + ")",
                          'avatar': "/contacts/" + (username or '') + ".gif",
                          'type': 'contact'
                         })
            Users.append(UserObject)

        #for User in Users:
         #   self.log.warning("%s\t%s\t%s\t%s\n", User['id'], User['name'], User['avatar'], User['type'])

        add_script_data(req, {
                              "UserList": Users
                             })    

        # Add js and css files
        notfound = True
        for kind, data, pos in stream:
            if kind == START and notfound:
                autocomplete = data[1].get('data-trac-mentions')
                if autocomplete:
                    notfound = False
                    if self.underscore_location:
                        add_script(req, self.underscore_href(
                                'underscore-min.js'))
                        add_stylesheet(req, 'mentions/jquery.mentionsInput.css')
                        add_script(req, 'mentions/jquery.mentionsInput.js')
                        add_script(req, 'mentions/mentions.js')
                    else:
                        self.log.warning("MentionsModule can't work because "
                                         "of missing configuration")
            yield kind, data, pos


    #IRequestFilter Methods

    def pre_process_request(self, req, handler):
        self.log.warning("\n\nEntered pre_process_request\n\n")
        self.log.warning('\nreq.args: %s\n', req.args)
        
        
        if req.args.get('view_time') is not None:    #Check if there is submit data by asking for 1 of its fields
                            
            #Read the fields that support wikiformatting
            CommentField = req.args.get('comment')
            DescriptionField = req.args.get('field_description')
            self.log.warning('\nComment: %s\nDesc: %s\n', CommentField, DescriptionField)
            
            #Parse the wikiformatting fields to get the mentioned users
            MentionedUsers = re.findall('(?<=@)[\w]+', CommentField) 
            for User in re.findall('(?<=@)[\w]+', DescriptionField):
                if User not in MentionedUsers:
                    MentionedUsers.append(User)
            
            self.log.warning('\nFound: \n%s', MentionedUsers)
            
            #Create the value for field_cc
            field_cc = req.args.get('field_cc')
            for User in MentionedUsers:
                if len(re.findall('^' + User + '(?=[\s,]|$)|(?<=[\s,])' + User + '(?=[\s,]|$)', field_cc)) == 0:  #Add the user to CC: if it is not already there
                    if len(field_cc) != 0:  #Add a ',' if there are already some users in the field
                        field_cc += ', '
                    field_cc += User
            
            #Modify the request field
            self.log.warning('\nmodified field_cc:%s\n', field_cc)
            req.args['field_cc'] = field_cc
            
        return handler

    def post_process_request(self, req, template, data, content_type):
        self.log.warning("\n\nEntered post_process_request\n\n")
        
        self.log.warning('\nreq.args: %s\n', req.args)

        self.log.warning('\ndata: %s\n', data)

        if data is not None:
            if req.args.get('view_time') is not None:    #Check if there is submit data by asking for 1 of its fields

                #Read the fields that support wikiformatting
                CommentField = req.args.get('comment')
                DescriptionField = req.args.get('field_description')
                self.log.warning('\nComment: %s\nDesc: %s\n', CommentField, DescriptionField)

                #Parse the wikiformatting fields to get the mentioned users
                MentionedUsers = re.findall('(?<=@)[\w]+', CommentField) 
                for User in re.findall('(?<=@)[\w]+', DescriptionField):
                    if User not in MentionedUsers:
                        MentionedUsers.append(User)

                self.log.warning('\nFound: \n%s', MentionedUsers)

                #Create the value for field_cc
                #cc_list = req.args.get('field_cc').split(',')
                #cc_list = [User.strip() for User in field_cc.split(',')]
                
                cc_list = Chrome(self.env).cc_list(req.args.get('field_cc'))
                
                for User in MentionedUsers:
                    if User not in cc_list:
                        cc_list.append(User)                
                
                field_cc = ','.join(cc_list)
                
                self.log.warning('\nmodified field_cc:%s\n', field_cc)


                #Add the created field_cc value to data dict
                if field_cc != req.args.get('field_cc') and data is not None: 
                    new_cc = {'new': field_cc, 
                              #'rendered': <Fragment>, 
                              'old': req.args.get('field_cc', ''), 
                              'by': req.authname, 
                              'label': 'Cc'}

                    if data.get('change_preview') is not None:
                        self.log.warning('\nchange preview:%s\n', data['change_preview'])
                        data['change_preview']['fields'].update({'cc': new_cc})

                    if data.get('description change') is not None:
                        self.log.warning('\ndescription change:%s\n', data['description_change'])
                        data['description change']['fields'].update({'cc' : new_cc})
                
                

        return template, data, content_type






