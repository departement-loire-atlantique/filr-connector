import base64
import datetime
from typing import OrderedDict
import requests
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


class Filr(BaseResource):
    category = "Divers"

    class Meta:
        verbose_name = "Connecteur pour Filr"

    api_description = "API pour Filr."

    # Création d'un objet contenant les praramètres pour ajouter un champs d'upload de document
    DOCUMENT_SCHEMA = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "Ajouter un document",
        "description": "",
        "type": "object",
        "required": ["demand_id", "document", "title"],
        "properties": OrderedDict({
            "demand_id": {
                "description": "Document title (docTitle)",
                "type": "string",
            },
            "title": {
                "description": "Document Title (docTitle)",
                "type": "string"
            },
            "filename": {
                "description": "Document filename (docFile)",
                "type": "string"
            },
            "document": {
                "type": "object",
                "description": "File object (file0)",
                "required": ["filename", "content_type", "content"],
                "properties": {
                    "filename": {
                        "type": "string"
                    },
                    "content_type": {
                        "type": "string",
                        "description": "MIME content-type"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content, base64 encoded"
                    }
                }
            }
        })
    }

    @endpoint()
    def info(self, request):
        return {"hello": "Filr!"}

    @endpoint(
        name = "add-document",
        description = "",
        perm = "can_access",
        methods = ["post"],
        post={
            "request_body": {
                "schema": {
                    "application/json": DOCUMENT_SCHEMA
                }
            }
        }
    )
    def add_document(self, request, post_data):
        endpoint = "api/export/document/test/" + post_data["demand_id"]
        filename = post_data.get("filename") or post_data["document"]["filename"]
        params = {
            "docTitle": post_data["title"],
            "docFile": filename
        }
        content = base64.b64decode(post_data["document"]["content"])
        content_type = post_data["document"]["content_type"]
        files = {
            "file0": (filename, content, content_type)
        }
        added = self.call(endpoint, method="post", params=params, files=files)
        return {"data": added}
        


    @endpoint(
        name="upload",
        methods=["post"],
        description=_("Upload a file"),
        parameters={
            "WFID": {
                "description": _("ID du worklow emetteur"),
                "example_value": "DIA-ENS",
            },
            "emails": {
                "description": _("emails des destinataires"),
                "example_value": "guillaume.gautier@loire-atlantique.fr;gru.loireatlantique+filr@gmail.com",
            },
            "login": {
                "description": _("Login Filr"),
                "example_value": "1234",
            },
            "password": {
                "description": _("Mot de passe Filr"),
                "example_value": "password",
            },
        },
        post={
            "request_body": {
                "schema": {
                    "application/json": DOCUMENT_SCHEMA
                }
            }
        }
    )
    def upload(self, request, WFID, emails, login, password):
        code, label, gid_per = self.call_select_appairage(login, password, email)
        if code in ["2", "3", "5"]:
            link, created = Link.objects.get_or_create(
                resource=self, name_id=NameID, id_per=id_per
            )
            return {"link_id": link.pk, "new": created, "code": code, "label": label}
        elif code == "6":
            raise APIError("unknown-login", data={"code": code, "label": label})
        elif code in ["4", "1"]:
            raise APIError("invalid-password", data={"code": code, "label": label})
