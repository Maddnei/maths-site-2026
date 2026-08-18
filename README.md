# 📐 Site Web Pédagogique - Mathématiques & Sciences 2026-2027
**Enseignant : M. Gimenez**  
**Identifiant enseignant :** `dgimenez`  
**Mot de passe par défaut :** `Cadolive+2406`

---

## 🌟 Présentation du projet

Ce site web a été spécialement conçu pour la gestion pédagogique de vos classes de lycée pour l'année scolaire 2026-2027 :
- **1 classe de Seconde** (Mathématiques & SNT)
- **2 classes de 1ère STMG** (1ère STMG 1 et 1ère STMG 2)
- **2 classes de 1ère Enseignement Scientifique** (1ère ES 1 et 1ère ES 2)

### 🎯 Fonctionnalités principales :
1. **Accueil clair et responsive :** Les élèves accèdent directement à leur classe depuis leur smartphone, tablette ou ordinateur.
2. **Tableau d'affichage dynamique par classe :** Publiez des annonces, devoirs à faire, dates de contrôles ou félicitez les meilleures notes aux devoirs surveillés (Tableau d'honneur).
3. **Organisation par chapitres modifiables :** Déposez facilement des cours, fiches d'exercices, devoirs maison (DM), corrigés officiels (fichiers PDF, PNG, JPG, JPEG) et des liens interactifs (GeoGebra, vidéos YouTube, simulateurs).
4. **Espace collaboratif "Exercices & Corrigés" pour les élèves :**
   - Les élèves peuvent prendre en photo directement avec leur téléphone l'**énoncé** d'un exercice et sa **correction** vue en classe.
   - Ils peuvent indiquer leur nom ou choisir de rester **anonymes**.
   - **Modération complète :** L'exercice reste en attente jusqu'à ce que vous le validiez dans votre centre de modération. Une fois validé, il devient instantanément visible par toute la classe avec zoom haute résolution.
5. **Mode Administrateur intuitif :** Connectez-vous avec `dgimenez` / `Cadolive+2406` pour ajouter des cours, créer des chapitres, modifier des classes et modérer les propositions d'élèves en 1 clic.

---

## 🚀 1. Lancement rapide sur votre ordinateur (Local)

Pour tester ou utiliser le site directement sur votre machine :

### Méthode 1 : En un seul double-clic (Windows)
Double-cliquez simplement sur le fichier **`lancer_site.bat`** présent dans ce dossier.  
Il s'occupe de tout :
1. Vérification des dépendances Python
2. Démarrage du serveur
3. Ouverture automatique de votre navigateur sur `http://localhost:5000`

### Méthode 2 : En ligne de commande
```bash
# 1. Ouvrir un terminal dans le dossier "site 2026"
# 2. Installer les dépendances :
python -m pip install -r requirements.txt

# 3. Lancer l'application :
python app.py
```
Accédez ensuite à l'adresse : **`http://localhost:5000`**

---

## 🌐 2. Guide complet : Comment héberger ce site 100% GRATUITEMENT avec plusieurs GO de stockage

Pour que vos élèves puissent accéder au site depuis chez eux ou en classe avec leur smartphone, voici la meilleure solution gratuite actuelle :

---

### ⭐ SOLUTION RECOMMANDÉE : Render.com (Hébergement web gratuit) + Cloudinary (25 Go de stockage gratuit)

Cette combinaison est la plus puissante, la plus simple et offre **25 Go de stockage gratuit** pour toutes les photos d'exercices et les fichiers PDF de vos élèves.

```
+------------------------------------+       +------------------------------------+
|            Render.com              |       |             Cloudinary             |
|   (Hébergement du site Flask)      | <---> |   (Stockage gratuit de 25 Go pour  |
|      100% Gratuit à vie            |       |    les photos d'élèves et PDF)     |
+------------------------------------+       +------------------------------------+
```

---

#### 📋 Étape A : Créer un compte GitHub (Gratuit)
1. Rendez-vous sur **[github.com](https://github.com)** et créez un compte gratuit si vous n'en avez pas.
2. Créez un nouveau dépôt (repository) privé ou public nommé `maths-site-2026`.
3. Déposez les fichiers de ce dossier `site 2026` sur votre dépôt GitHub (via GitHub Desktop, Git en ligne de commande ou simplement en glissant-déposant les fichiers sur l'interface web de GitHub).

---

#### 📋 Étape B : Créer un compte Cloudinary pour le stockage des photos (25 Go Gratuits)
1. Rendez-vous sur **[cloudinary.com](https://cloudinary.com)** et cliquez sur **Sign Up for Free**.
2. Une fois connecté sur votre tableau de bord (Dashboard), repérez vos identifiants dans la section **Product Environment Credentials** :
   - **Cloud Name** (ex: `dxy123abc`)
   - **API Key** (ex: `123456789012345`)
   - **API Secret** (ex: `abcdefghijklmnopqrstuvwxyz`)
   - Ou directement l'**API Environment variable** (`CLOUDINARY_URL=cloudinary://...`)
3. *Note : Grâce au module `storage.py` déjà inclus dans le projet, dès que ces variables sont configurées, tous les fichiers et photos d'élèves sont automatiquement envoyés sur votre espace Cloudinary sécurisé.*

---

#### 📋 Étape C : Déployer le site sur Render.com (Gratuit)
1. Rendez-vous sur **[render.com](https://render.com)** et créez un compte gratuit (vous pouvez vous connecter directement avec votre compte GitHub).
2. Cliquez sur le bouton bleu **New +** en haut à droite, puis sélectionnez **Web Service**.
3. Choisissez **Build and deploy from a Git repository** et sélectionnez votre dépôt `maths-site-2026`.
4. Remplissez les champs de configuration :
   - **Name :** `maths-gimenez` (ou le nom de votre choix)
   - **Region :** `Frankfurt (EU Central)` (le plus proche pour la France)
   - **Branch :** `main`
   - **Runtime :** `Python 3`
   - **Build Command :** `pip install -r requirements.txt`
   - **Start Command :** `gunicorn app:app`
   - **Instance Type :** `Free` ($0/month)
5. Déroulez la section **Environment Variables** (Variables d'environnement) et ajoutez :
   - `ADMIN_USERNAME` : `dgimenez`
   - `ADMIN_PASSWORD` : `Cadolive+2406` (ou votre mot de passe personnalisé)
   - `SECRET_KEY` : une suite de lettres et chiffres aléatoires (ex: `maths2026cleSecreteSuperSecurisee`)
   - `CLOUDINARY_URL` : collez l'URL fournie par Cloudinary (ex: `cloudinary://123456:abcdef@dxy123abc`)
6. Cliquez sur **Deploy Web Service**.

En 2 minutes, votre site est en ligne avec une adresse sécurisée HTTPS du type :  
👉 **`https://maths-gimenez.onrender.com`**

Vous pouvez communiquer cette adresse à tous vos élèves !

---

### 💡 Alternative 100% sans carte bancaire : PythonAnywhere.com
Si vous préférez une interface web tout-en-un sans passer par GitHub :
1. Créez un compte gratuit sur **[pythonanywhere.com](https://www.pythonanywhere.com)** (offre "Beginner" gratuite avec 512 Mo de stockage).
2. Uploadez vos fichiers dans l'onglet **Files**.
3. Dans l'onglet **Web**, ajoutez une nouvelle application web Python 3.11 avec Flask et pointez vers `app.py`.
4. Votre site est accessible gratuitement sur `https://dgimenez.pythonanywhere.com`.

---

## 🛠️ 3. Guide d'utilisation du site pour l'enseignant

### 🔐 Se connecter en tant que professeur
1. Cliquez sur le bouton **"Espace Professeur"** en haut à droite de n'importe quelle page.
2. Saisissez vos identifiants :
   - **Identifiant :** `dgimenez`
   - **Mot de passe :** `Cadolive+2406`
3. Une fois connecté, un bandeau orange apparaît en haut de l'écran avec l'accès direct aux outils de gestion et les boutons d'édition rapide sur chaque page.

---

### 📥 Valider les exercices proposés par les élèves
1. Lorsqu'un élève soumet une photo d'énoncé et de corrigé, une notification avec un badge rouge apparaît dans la barre d'administration.
2. Cliquez sur **"Modération élèves"** dans le bandeau supérieur (ou rendez-vous dans le chapitre concerné).
3. Vous pouvez visualiser côte à côte la photo de l'énoncé et la photo de la correction en haute définition.
4. Cliquez sur :
   - **"Valider et publier"** : L'exercice et le corrigé deviennent immédiatement visibles par tous les élèves dans le chapitre concerné avec la mention de l'élève (ou mention anonyme).
   - **"Rejeter"** : La proposition est archivée et n'apparaît pas pour les élèves.
   - **"Supprimer"** : Supprime définitivement la proposition.

---

### 📚 Déposer un document ou un lien internet dans un chapitre
1. Rendez-vous sur la classe puis sur le chapitre souhaité.
2. Cliquez sur **"Ajouter un document / lien"**.
3. Renseignez :
   - Le titre du document (ex: *Cours - Dérivation et variations*, *DM n°2 pour le 15 octobre*)
   - La catégorie (*Cours, Fiche d'exercices, Devoir Maison, Corrigé, Fiche méthode, Lien web*)
   - Le fichier (PDF, image PNG, JPG) ou l'URL (lien GeoGebra, vidéo YouTube explicative...)
4. Cliquez sur **Ajouter la ressource**. Le document est immédiatement disponible en téléchargement pour les élèves.

---

### 📢 Publier une annonce ou afficher les meilleures notes
1. Sur la page d'accueil ou sur la page d'une classe, cliquez sur **"Ajouter une annonce / info"**.
2. Choisissez la destination (*Toutes les classes* ou *Une classe spécifique*).
3. Choisissez le type :
   - 🏆 **Félicitations / Meilleures notes** (affiche un badge doré pour valoriser les élèves)
   - 📝 **Contrôle / DS** (annonce de date d'évaluation)
   - 📌 **Devoir à rendre**
   - 📢 **Information générale**
4. Rédigez votre message et cochez si besoin *Épingler en haut du tableau*.

---

### ⚙️ Ajouter ou modifier des classes et des chapitres
- **Gérer les classes :** Cliquez sur **"Gérer les classes"** dans le bandeau supérieur pour renommer une classe, changer son icône ou son ordre d'affichage.
- **Ajouter un chapitre :** Sur la page d'une classe, cliquez sur **"Nouveau chapitre"** pour créer un nouveau thème du programme.

---

### 🔄 Modifier l'année scolaire & Réinitialisation en 1 clic en fin d'année
Dans la barre d'administration en haut, cliquez sur **"Paramètres & Fin d'année"** :
1. **Modifier la date / l'année scolaire facilement :**
   - Vous pouvez changer le texte de l'année scolaire (ex: `2026-2027`, `2027-2028`, etc.) et le nom affiché à tout moment sans toucher au code.
2. **Bouton de fin d'année (Nouvelle rentrée) :**
   - **Option Rentrée Propre (Recommandée) :** En 1 clic, le site efface toutes les propositions et photos d'exercices des anciens élèves, nettoie les anciennes annonces et notes de l'année terminée, ajoute un message d'accueil pour la nouvelle rentrée, et passe à l'année suivante (ex: 2027-2028). **Tous vos cours, chapitres, polycopiés et liens sont précieusement conservés !**
   - **Option Vider les exercices élèves :** Efface uniquement les photos d'exercices soumises par les élèves.
   - **Option Remise à zéro d'usine :** Remet le site totalement à neuf.
   - *Sécurité intégrée : une confirmation vous demande de taper `REINITIALISER` pour éviter toute fausse manipulation.*

---

## 📁 4. Structure des fichiers du projet

```
site 2026/
├── app.py                 # Application principale Flask (routes, sécurité, modération)
├── config.py              # Configuration (identifiants, chemins, clés d'API)
├── database.py            # Base de données SQLite (classes, chapitres, documents, propositions)
├── storage.py             # Gestionnaire de fichiers (Stockage local + Cloudinary 25 Go)
├── static/
│   ├── css/
│   │   └── custom.css     # Styles personnalisés et animations
│   ├── js/
│   │   └── main.js        # Gestion des fenêtres modales, zoom photo (lightbox), aperçus
│   └── uploads/           # Dossier de stockage local des documents et photos
│       ├── documents/     # Cours et polycopiés PDF du professeur
│       ├── exercises/     # Photos d'énoncés envoyées par les élèves
│       └── solutions/     # Photos de corrigés envoyées par les élèves
├── templates/             # Pages HTML avec Tailwind CSS responsive
│   ├── base.html          # Structure générale, barre de navigation et pied de page
│   ├── index.html         # Page d'accueil avec choix des classes et guide élèves
│   ├── class.html         # Tableau d'affichage et liste des chapitres d'une classe
│   ├── chapter.html       # Cours du professeur et espace collaboratif d'exercices corrigés
│   ├── admin_mod.html     # Centre de modération des propositions d'élèves
│   ├── admin_classes.html # Gestionnaire des classes
│   ├── admin_login.html   # Page de connexion de l'enseignant
│   └── 404.html           # Page d'erreur 404
├── requirements.txt       # Liste des dépendances Python (Flask, Pillow, Cloudinary, etc.)
├── lancer_site.bat        # Raccourci Windows pour lancer le site en 1 clic
├── Procfile               # Fichier de déploiement pour Render / Koyeb / Heroku
├── runtime.txt            # Version de Python pour l'hébergement cloud
├── .gitignore             # Fichiers ignorés par Git
└── README.md              # Ce guide d'installation et d'utilisation
```

---

## 🔒 5. Sécurité et sauvegarde

- **Changement de mot de passe :** Vous pouvez modifier votre mot de passe à tout moment dans le fichier `config.py` ou via la variable d'environnement `ADMIN_PASSWORD`.
- **Sauvegarde de la base de données :** Toutes les données (classes, chapitres, annonces, liens) sont stockées dans le fichier léger `site.db`. Pour faire une sauvegarde complète de votre site, il vous suffit de copier ce fichier `site.db` sur une clé USB ou un disque externe.
- **Photos et documents :** Avec Cloudinary, vos images et PDF sont automatiquement sauvegardés et distribués via un réseau CDN rapide et sécurisé.
