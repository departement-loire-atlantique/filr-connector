# Spécifications connecteur Filr pour Publik

Dans le cadre du formulaire DIA-ENS, on veut pouvoir utiliser le service Filr ([transfert.loire-atlantique.fr](https://transfert.loire-atlantique.fr/)) afin de mettre à disposition des fichiers issus de Publik à des partenaires extérieurs. Ces partenaires n'auront pas accès au back-office de Publik. Ils recevront un courriel avec un lien leur permettant d'accéder au dossier dans Filr disposant des fichiers les concernants. Ce lien sera privé et valable pour 30 jours (par défaut). Au bout des 30 jours, le lien sera expiré et les partenaires n'auront plus accès aux fichiers.

## Paramètres du connecteur

Créer le code du connecteur afin que l'on puisse ajouter le connecteur dans Passerelle à cette URL :
https://passerelle.dev.publik.love/manage/filr/add

En plus des champs *titre*, *Identifiant* et *Description*, ajouter :

* *Identifiant d'authentification basique*
* *Mot de passe pour l'authentification basique*

Ces champs permettent d'indiquer les identifiants de Filr. En attendant la création d'identifiants spécifiques Filr pour Publik, indiquer ses propres identifiants.

*  *URL de base du webservice*

    Avec la remarque : URL de base de l'API (par exemple : https://transfert.loire-atlantique.fr/)

Pour utiliser le connecteur dans Publik, on passe par des actions de Webservice vers des endpoints décrits ci-dessous.

## Ajout de fichiers dans Filr

* Endpoint : **upload**
* URL de la requête : `{{passerelle_url}}filr/IDENTIFIANT/upload`
* Méthode : `POST (JSON)`
* Données à envoyer dans le corps de la requête :
    * *document* : `{{ form_var_fichier_formulaire }}` (gabarit)
    * *filename* : `NOM_FICHIER.EXT` (gabarit)
    * *folder_name* : `NOM_DOSSIER` (texte)

Récupère le document et le transfère dans Filr avec le nom *filename* dans le dossier *folder_name/n° de la demande*.

Le n° de la demande est le n° donné par la variable du formulaire *form_number_raw*.

Si *filename* n'est pas indiqué, utiliser l'attribut *filename* du *document*.

Si *folder_name* n'est pas indiqué, utiliser le *form_slug* courant.

Si plusieurs fichiers sont à transférer, on fait pour chaque fichier une requête séparée.

## Partage d'un lien Filr de téléchargement

* Endpoint : **share**
* URL de la requête : `{{passerelle_url}}filr/IDENTIFIANT/share`
* Méthode : `POST (JSON)`
* Données à envoyer dans le corps de la requête :
    * *emails* : emails des destinaires du lien de partage, séparés par des virgules
    * *folder_name* : `NOM_DOSSIER` (texte)
    * *days_to_expire* : nombre de jours avant expiration du lien

Créé un lien de partage privé avec envoi de mail aux destinataires indiqués dans *emails* pour le dossier : *folder_name/n° de la demande*.

Si *folder_name* n'est pas indiqué, utiliser le *form_slug* courant.

Si *days_to_expire* est indiqué à 0, ne pas indiquer d'expiration pour le lien de partage. Si *days_to_expire* n'est pas indiqué, indiquer par défaut 30 jours d'expiration.

## Suppression d'un dossier dans Filr

* Endpoint : **delete_folder**
* URL de la requête : `{{passerelle_url}}filr/IDENTIFIANT/delete_folder`
* Méthode : `POST (JSON)`
* Données à envoyer dans le corps de la requête :
    * *folder_name* : `NOM_DOSSIER` (texte)

Supprime le dossier : *folder_name/n° de la demande*. **Attention** : ne pas supprimer le dossier racine *folder_name* mais seulement le sous-dossier correspondant au n° de la demande !

## Gestion des erreurs

Créer dans le workflow un statut technique appelé *Erreur Filr* visible seulement par le rôle *Support technique*. En cas d'erreur, sauter dans ce statut et logguer l'erreur dans ce statut. À la charge du workflow de prévoir de relancer les opérations, par exemple par une action manuelle d'un gestionnaire ou administrateur fonctionnel.

Dans l'action du web-service, cocher l'option *Notifier en cas d'erreur*, afin qu'un courriel de notification soit envoyé au courriel indiqué dans l'option *Courriel pour les tracebacks* dans les paramètres de l'environnement, partie *Options de debug*.

En cas d'avertissement de Filr, l'afficher dans un commentaire visible seulement du support technique dans le statut suivant l'appel au web-service.

Pour afficher les erreurs Filr, se conformer au [format attendu décrit dans la documentation de Publik](https://doc-publik.entrouvert.com/dev/echanges-logiciel-de-demandes-metier/#Format-des-r%C3%A9ponses-en-cas-derreur).
