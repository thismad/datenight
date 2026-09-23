# datenight ✈️💘

Page de présentation des premières vacances (28–31 juillet) : quatre destinations, avantages et inconvénients, et un final façon Tinder où elle « like » sa destination préférée puis remplit un formulaire pour la réservation (billets d'avion, logement, allergies).

**Page en ligne** : https://thismad.github.io/datenight/

## Structure

- `template.html` — contenu de la page (styles, sections, script). C'est le fichier à modifier.
- `build.py` — enveloppe le template en document HTML complet (balises `og:` pour l'aperçu WhatsApp, favicon, `noindex`).
- `index.html` — fichier généré, servi par GitHub Pages. Ne pas modifier à la main.
- `img/` — photos (Wikimedia Commons, recompressées).
- `template-ischia.html`, `template-ischia-memories.html`, `template-trips.html` : itinéraire (`/ischia/`), souvenirs (`/ischia/memories/`) et liste des voyages (`/trips/`). La navbar (Trip Ideas / Finished Trips) est ajoutée par `build.py` sur toutes les pages.
- `media/<voyage>/` : photos et clips des souvenirs, préparés avec `python3 scripts/prep_media.py SOURCE media/<voyage>/nom.jpg` (ou `.mp4` pour un clip en boucle muet, 15 s max). Le script supprime les données GPS.

## Modifier la page

```bash
# 1. Éditer template.html
# 2. Regénérer :
python3 build.py
# 3. Commit + push : GitHub Pages se met à jour en ~1 minute
```

## Formulaire

Le formulaire final envoie les réponses par email à `mathis.dehez@gmail.com` via [FormSubmit](https://formsubmit.co) (aucun serveur nécessaire).

⚠️ **Activation requise** : la toute première soumission déclenche un email de confirmation de FormSubmit — cliquer le lien d'activation, sinon rien n'arrive. Faire soi-même une soumission de test avant d'envoyer le lien.

Après activation, FormSubmit fournit un alias aléatoire (ex. `formsubmit.co/abc123...`) qui peut remplacer l'adresse email en clair dans `template.html` pour ne pas l'exposer dans le code source.

## Crédits photos

Photos issues de Wikimedia Commons (licences libres, auteurs divers) : Castello Aragonese, Sant'Angelo, baie de San Montano, Corricella (Procida), Chambord, Chenonceau, Villandry, Cheverny, Porto Timoni, monastère de Vlacherna, Corfou-ville, Agios Gordios, Bellagio, Villa del Balbianello, Nesso, lungolago de Bellagio.
