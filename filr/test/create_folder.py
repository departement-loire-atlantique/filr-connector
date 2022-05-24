import base64
import binascii
import datetime
import json
import requests

from urllib.parse import urljoin

def getFilrFolderId(base_url, username, password, form_name):

        # ID du dossier publik
        # de recette
        publik_folder_id = "892837"
        # de prod
        if username == "publik-prod":
            publik_folder_id = "892847"

        url_filr_list_folders = f"{base_url}rest/folders/{publik_folder_id}/library_folders"
        r = requests.get(url_filr_list_folders, auth=(username, password))
        folder_id = 0
        i = 0
        items = json.loads(r.content)
        for item in items["items"][i:]:
            print(f"title = {item['title']}")
            folder_name = item["title"]
            # Vérification du nom de l'objet parcouru
            if folder_name == form_name:
                # Un dossier existe avec le nom du formulaire concerné,
                # On donne l'id du dossier à la variable folder_id et on sort de la boucle
                folder_id = item["id"]
                # Et on sort de la boucle
                break
            i += 1

        # On vérifie que folder_id est différent de 0 (càd qu'un id a bien été récupérer)
        if folder_id != 0:
            # On renvoie l'id
            print(f"Le dossier {form_name} existe déjà, son ID est {folder_id}")
            return folder_id
        else:
            # Sinon on crée un dossier avec le nom du formulaire
            print(f"Le dossier {form_name} n'existe pas, on le créé")
            url_filr_create_folder = f"{base_url}rest/folders/{publik_folder_id}/library_folders"
            print(f"url_filr_create_folder = {url_filr_create_folder}")
            headers = {"Content-Type": "application/json"}
            content = {"title": form_name}
            created_folder = requests.post(url_filr_create_folder, auth=(username, password), data=json.dumps(content), headers=headers)
            result = json.loads(created_folder.content)
            # Et on renvoie l'id du nouveau dossier
            folder_id = result['id']
            print(f"ID dossier créé = {folder_id}")
            return folder_id
        
def main():
    base_url = "https://transfert.loire-atlantique.fr/"
    username = "publik-recette"
    password = "wdNyxltxggSi"
    form_name = "dia-ens"
    folder_id = getFilrFolderId(base_url, username, password, form_name)

if __name__ == "__main__":
    main()