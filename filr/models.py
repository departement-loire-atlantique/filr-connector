import base64
import binascii
import datetime
import requests

from collections import OrderedDict

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import six
from django.utils.six.moves.urllib import parse as urlparse
from django.utils.translation import ugettext_lazy as _

from passerelle.base.models import BaseResource, HTTPResource
from passerelle.utils import xml as xmlutils
from passerelle.utils.api import endpoint
from passerelle.utils.conversion import to_ascii
from passerelle.utils.jsonresponse import APIError
from passerelle.utils.validation import is_number

ADD_DOCUMENT_SCHEMA = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'File to upload',
    'description': '',
    'type': 'object',
    'required': ['folder_id', 'login', 'password', 'document'],
    'properties': OrderedDict(
        {
            'folder_id': {
                'description': 'Filr folder',
                'type': 'string',
            },
            'login': {
                'description': 'Filr login',
                'type': 'string',
            },
            'password': {
                'description': 'Filr password',
                'type': 'string',
            },
            'filename': {
                'description': 'Filr filename',
                'type': 'string',
            },
            'document': {
                'type': 'object',
                'description': 'File object (file0)',
                'required': ['filename', 'content_type', 'content'],
                'properties': {
                    'filename': {
                        'type': 'string',
                        'description': 'Filr filename',
                    },
                    'content_type': {
                        'type': 'string',
                        'description': 'MIME content-type',
                    },
                    'content': {
                        'type': 'string',
                        'description': 'Content, base64 encoded',
                    },
                },
            },
        }
    ),
}

class Filr(BaseResource):
    category = "Divers"

    class Meta:
        verbose_name = "Connecteur pour Filr"

    api_description = "API pour Filr."

    @endpoint()
    def info(self, request):
        return {"hello": "Filr! ça marche"}

    @endpoint(perm="can_access")
    def upload(self, request):
        return {"hello": "Filr upload!"}

    @endpoint(
        name="upload",
        perm='can_access',
        methods=["post"],
        description=_("Upload a file"),
        post={'request_body': {'schema': {'application/json': ADD_DOCUMENT_SCHEMA}}},
        display_category=_('Demand'),
        display_order=1,
    )

    def upload(self, request, post_data):

        login = post_data.get('login')
        password = post_data.get('password')
        filename = post_data.get('filename') or post_data['document']['filename']
        endpoint = 'https://transfert.loire-atlantique.fr/rest/folders/' + post_data['folder_id'] + '/library_files?file_name=' + filename
        content = base64.b64decode(post_data['document']['content'])
        headers = {'content-type': 'application/octet-stream'}
        r = requests.post(endpoint, auth=(login, password), data=content, headers=headers)
        return {'data': {"commentaire": r.text}}
