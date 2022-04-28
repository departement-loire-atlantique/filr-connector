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
from passerelle.compat import json_loads
from passerelle.utils.jsonresponse import APIError
from passerelle.utils.validation import is_number

ADD_DOCUMENT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "File to upload",
    "description": "",
    "type": "object",
    "required": ["form_name", "document"],
    "properties": OrderedDict(
        {
            "form_name": {
                "description": "Form name",
                "type": "string"
            },
            "filename": {
                "description": "Filr filename",
                "type": "string",
            },
            "document": {
                "type": "object",
                "description": "File object (file0)",
                "required": ["filename", "content_type", "content"],
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Filr filename",
                    },
                    "content_type": {
                        "type": "string",
                        "description": "MIME content-type",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content, base64 encoded",
                    },
                },
            },
        }
    ),
}


def getFilrFolderId(base_url, username, password, requestData, logger):
        url_filr = urlparse.urljoin(base_url, "/rest/folders")
        try:
            payload = json_loads(requestData.body)
        except (ValueError):
            raise APIError("Invalid payload format: json expected")

        r = requests.get(url_filr, auth=(username, password))
        folderId = 0
        i = 1 # On initialise à 1 pour sauter le premier item trouver dans Filr qui correspond à "Stockage Mes fichiers"
        items = json_loads(r.content)
        for item in items["items"][i:]:
            folderName = item["title"]
            # Vérification du nom de l'objet parcouru
            if folderName == payload["form_name"]:
                # Un dossier existe avec le nom du formulaire concerné,
                # On donne l'id du dossier à la variable folderId et on sort de la boucle
                folderId = item["id"]
                
                # Et on sort de la boucle
                break
                
            i += 1
            
        logger.info(f"DEBUG : Sortie de la boucle for, tous les items ont été parcouru.")
        
        # On vérifie que folderId est différent de 0 (càd qu'un id a bien été récupérer)
        if folderId != 0:
            # On renvoie l'id
            return folderId
        else:
            # Sinon on crée un dossier avec le nom du formulaire
            creationUrl = f"{url_filr}/{item['id']}/library_folder"
            headers = {"content-type": "application/json"}
            content = {"title": payload["form_name"]}
            createFolder = requests.post(creationUrl, auth=(username, password), data=content, headers=headers)
            try:
                result = createFolder.content
            except (ValueError):
                raise APIError("Invalid payload format: json expected")
            # Et on renvoie l'id du nouveau dossier
            return result["id"]
        

class Filr(BaseResource, HTTPResource):
    category = "Divers"

    class Meta:
        verbose_name = "Connecteur pour Filr"

    api_description = "API pour Filr."

    base_url_filr = models.URLField(
        verbose_name=_("URL API Filr"),
        help_text=_("URL de base de l\"API Filr (example: https://transfert.loire-atlantique.fr/)"),
        default="https://transfert.loire-atlantique.fr/",
    )

    @endpoint()
    def info(self, request):
        return {"hello": "Filr! ça marche"}

    @endpoint(perm="can_access")
    def upload(self, request):
        return {"hello": "Filr upload!"}

    @endpoint(
        name = "upload",
        perm = "can_access",
        methods = ["post"],
        description = _("Upload a file"),
        post = {
            "request_body": {
                "schema": {
                    "application/json": ADD_DOCUMENT_SCHEMA
                }
            }
        },
        display_category =_("Demand"),
        display_order = 1,
    )

    def upload(self, request, post_data):
        folder_id = getFilrFolderId(self.base_url_filr, self.basic_auth_username, self.basic_auth_password, request, self.logger)
        self.logger.info(f"DEBUG : {folder_id}")
        """ filename = post_data.get("filename") or post_data["document"]["filename"]
        url_filr = urlparse.urljoin(self.base_url_filr, f"/rest/folders/{folder_id}/library_files?file_name={filename}")
        content = base64.b64decode(post_data["document"]["content"])
        headers = {"content-type": "application/octet-stream"}
    
        r = requests.post(url_filr, auth=(self.basic_auth_username, self.basic_auth_password), data=content, headers=headers)
        
        return {
            "data": {
                "folderId": folder_id,
                "commentaire": r.text
            }
        } """
