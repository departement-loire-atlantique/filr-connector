import base64
import binascii
import datetime
import json
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
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "File to upload",
    "description": "",
    "type": "object",
    "required": ["form_name", "document"],
    "properties": OrderedDict(
        {
            "form_name": {"description": "Form name", "type": "string"},
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


def create_filr_folder(
    base_url, username, password, parent_folder_id, folder_name, logger
):

    url_filr_list_folders = f"{base_url}rest/folders/{parent_folder_id}/library_folders"
    r = requests.get(url_filr_list_folders, auth=(username, password))
    folder_id = 0
    i = 0
    items = json.loads(r.content)
    for item in items["items"][i:]:
        # Vérification du nom de l'objet parcouru
        if folder_name == item["title"]:
            # Un dossier existe avec le nom du formulaire concerné,
            # On donne l'id du dossier à la variable folder_id et on sort de la boucle
            folder_id = item["id"]
            # Et on sort de la boucle
            break
        i += 1

    # On vérifie que folder_id est différent de 0 (càd qu'un id a bien été récupérer)
    if folder_id != 0:
        # On renvoie l'id
        logger.info(f"Le dossier {folder_name} existe déjà, son ID est {folder_id}")
        return folder_id
    else:
        # Sinon on crée un dossier avec le nom du formulaire
        logger.info(f"Le dossier {folder_name} n'existe pas, on le créé")
        url_filr_create_folder = (
            f"{base_url}rest/folders/{parent_folder_id}/library_folders"
        )
        logger.info(f"url_filr_create_folder = {url_filr_create_folder}")
        headers = {"Content-Type": "application/json"}
        content = {"title": folder_name}
        created_folder = requests.post(
            url_filr_create_folder,
            auth=(username, password),
            data=json.dumps(content),
            headers=headers,
        )
        result = json.loads(created_folder.content)
        # Et on renvoie l'id du nouveau dossier
        folder_id = result["id"]
        logger.info(f"ID dossier créé = {folder_id}")
        return folder_id


def create_filr_folders(base_url, username, password, form_name, form_number, logger):
    # ID du dossier publik
    # de recette
    publik_folder_id = "892837"
    # de prod
    if username == "publik-prod":
        publik_folder_id = "892847"

    # Création du dossier correspondant au nom du formulaire
    form_name_folder_id = create_filr_folder(
        base_url,
        username,
        password,
        parent_folder_id=publik_folder_id,
        folder_name=form_name,
        logger=logger,
    )

    # Création du dossier correspondant au numéro du formulaire
    form_number_folder_id = create_filr_folder(
        base_url,
        username,
        password,
        parent_folder_id=form_name_folder_id,
        folder_name=form_number,
        logger=logger,
    )

    return form_number_folder_id


class Filr(BaseResource, HTTPResource):
    category = "Divers"

    class Meta:
        verbose_name = "Connecteur pour Filr"

    api_description = "API pour Filr."

    base_url_filr = models.URLField(
        verbose_name=_("URL API Filr"),
        help_text=_(
            'URL de base de l"API Filr (example: https://transfert.loire-atlantique.fr/)'
        ),
        default="https://transfert.loire-atlantique.fr/",
    )

    @endpoint()
    def info(self, request):
        return {"hello": "Filr! ça marche"}

    @endpoint(perm="can_access")
    def upload(self, request):
        return {"hello": "Filr upload!"}

    @endpoint(
        name="upload",
        perm="can_access",
        methods=["post"],
        description=_("Upload a file"),
        post={"request_body": {"schema": {"application/json": ADD_DOCUMENT_SCHEMA}}},
        display_category=_("Demand"),
        display_order=1,
    )
    def upload(self, request, post_data):

        form_name = post_data["form_name"]
        form_number = post_data["form_number"]

        folder_id = create_filr_folders(
            self.base_url_filr,
            self.basic_auth_username,
            self.basic_auth_password,
            form_name,
            form_number,
            self.logger,
        )

        filename = post_data.get("filename") or post_data["document"]["filename"]
        url_filr_upload_file = f"{self.base_url_filr}rest/folders/{folder_id}/library_files?file_name={filename}"
        content = base64.b64decode(post_data["document"]["content"])
        headers = {"content-type": "application/octet-stream"}
        r = requests.post(
            url_filr_upload_file,
            auth=(self.basic_auth_username, self.basic_auth_password),
            data=content,
            headers=headers,
        )
        return {"data": {"commentaire": r.text}}
