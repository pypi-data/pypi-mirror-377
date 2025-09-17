# 🐍 Sharokey Python SDK

> **Zero Knowledge secret sharing** - API cohérente avec les commandes CLI

## 🚀 Installation

```bash
pip install sharokey
```

## ⚡ Démarrage rapide

```python
import asyncio
import sharokey

async def main():
    # Configuration (équivalent: sharokey config --token xxx)
    client = sharokey.SharokeyClient(token="votre-token")
    
    # Créer un secret (équivalent: sharokey create "secret" --hours 24 --views 1)
    secret = await client.create("Mon secret confidentiel", 24, 1)
    print(f"URL de partage: {secret.share_url}")
    
    # Lister les secrets (équivalent: sharokey list)
    secrets = await client.list()
    print(f"Total: {secrets.count} secrets")

asyncio.run(main())
```

---

## 📚 API - Cohérente avec CLI

### Configuration

```python
import sharokey

# Configuration de base
client = sharokey.SharokeyClient(
    token="votre-token-api",           # REQUIS
    api_url="https://...",             # Optionnel (défaut: production)
    timeout=30                         # Optionnel (défaut: 30s)
)
```

### Créer un secret

```python
# Secret simple (équivalent: sharokey create "message" --hours 24 --views 1)
secret = await client.create("Mon mot de passe secret", 24, 1)
print(f"URL: {secret.share_url}")
print(f"Expire le: {secret.expiration}")

# Avec toutes les options (équivalent: sharokey create --description ... --otp-email ...)
secret = await client.create(
    "Informations critiques",
    hours=2,
    views=3,
    description="Accès serveur production",
    message="À utiliser dans les 2 heures",
    password="protection-additionnelle",
    otp_email="admin@entreprise.com"  # OTP par email
)

# Avec OTP SMS
secret = await client.create(
    "Code d'accès",
    hours=1,
    views=1,
    otp_phone="+33674747474"  # OTP par SMS
)

# Avec pièces jointes (équivalent: sharokey create --attach fichier1 --attach fichier2)
secret = await client.create(
    "Documents confidentiels",
    hours=48,
    views=5,
    description="Contrat et annexes",
    attachments=["contrat.pdf", "conditions.docx"],  # Chemins vers fichiers
    password="protection2024"
)
```

### Lister les secrets

```python
# Lister tous (équivalent: sharokey list)
secrets = await client.list()
print(f"{secrets.count} secrets trouvés")

# Avec filtres (équivalent: sharokey list --status active --limit 10)
secrets = await client.list(
    status='active',
    limit=10,
    creator='admin@example.com',
    search='serveur'
)

# Parcourir les résultats
for secret in secrets.data:
    vues_restantes = secret.maximum_views - secret.current_views
    print(f"{secret.slug}: {secret.description} ({vues_restantes} vues restantes)")
```

### Détails d'un secret

```python
# Obtenir les détails (équivalent: sharokey get ABC123)
secret = await client.get("ABC123XYZ")

print(f"Description: {secret.description}")
print(f"Créateur: {secret.creator}")
print(f"Vues: {secret.current_views}/{secret.maximum_views}")
print(f"Expire le: {secret.expiration}")
print(f"Pièces jointes: {secret.has_attachments}")
```

### Supprimer un secret

```python
# Supprimer (équivalent: sharokey delete ABC123)
success = await client.delete("ABC123XYZ")
if success:
    print("Secret supprimé avec succès")
```

### Statistiques

```python
# Obtenir les stats (équivalent: sharokey stats)
stats = await client.stats()

print(f"Total secrets: {stats.total_secrets}")
print(f"Secrets actifs: {stats.active_secrets}")
print(f"Secrets expirés: {stats.expired_secrets}")
print(f"Total vues: {stats.total_views}")
```

---

## 🔧 Fonctions utilitaires

### Tester la connectivité

```python
# Tester la connexion API
connected = await client.test_connection()
if not connected:
    print("Impossible de se connecter à Sharokey")
```

---

## 💡 Exemples pratiques

### Script d'automatisation

```python
#!/usr/bin/env python3
import asyncio
import sharokey
from pathlib import Path

async def deploy_credentials():
    """Déployer des identifiants de manière sécurisée."""
    
    client = sharokey.SharokeyClient(token="votre-token")
    
    # Créer un secret pour les identifiants de déploiement
    secret = await client.create(
        "DB_PASSWORD=super_secret_pwd",
        hours=1,  # Expire dans 1 heure
        views=1,  # Une seule vue
        description="Identifiants base de données - déploiement",
        otp_email="devops@entreprise.com"
    )
    
    print(f"🔐 Identifiants créés: {secret.share_url}")
    return secret.share_url

# Utilisation
if __name__ == "__main__":
    url = asyncio.run(deploy_credentials())
    print(f"Envoyez cette URL à l'équipe: {url}")
```

### Partage de fichiers sécurisé

```python
import asyncio
import sharokey
from pathlib import Path

async def share_files():
    """Partager des fichiers de manière sécurisée."""
    
    client = sharokey.SharokeyClient(token="votre-token")
    
    # Fichiers à partager
    files = [
        "documents/contrat.pdf",
        "documents/specifications.docx", 
        "documents/budget.xlsx"
    ]
    
    # Créer le secret avec attachments
    secret = await client.create(
        "Dossier client ABC - documents contractuels",
        hours=72,  # 3 jours
        views=10,  # 10 consultations max
        description="Documents contrat client ABC Corp",
        attachments=files,
        password="ContratABC2024",
        otp_email="commercial@entreprise.com"
    )
    
    print(f"📎 Dossier partagé: {secret.share_url}")
    print(f"📄 {len(files)} fichiers joints")
    print(f"🔒 Protégé par mot de passe et OTP email")
    
    return secret

# Utilisation
asyncio.run(share_files())
```

### Dashboard de monitoring

```python
import asyncio
import sharokey

async def dashboard():
    """Dashboard simple des secrets."""
    
    client = sharokey.SharokeyClient(token="votre-token")
    
    # Obtenir les statistiques
    stats = await client.stats()
    
    print("📊 DASHBOARD SHAROKEY")
    print("=" * 40)
    print(f"Total secrets:     {stats.total_secrets:>8}")
    print(f"Secrets actifs:    {stats.active_secrets:>8}")
    print(f"Secrets expirés:   {stats.expired_secrets:>8}")
    print(f"Total vues:        {stats.total_views:>8}")
    print()
    
    # Lister les secrets récents
    recent = await client.list(limit=5)
    print("🔐 SECRETS RÉCENTS")
    print("=" * 40)
    
    for secret in recent.data:
        status = "🟢 Actif" if secret.current_views < secret.maximum_views else "🔴 Épuisé"
        print(f"{secret.slug} | {status} | {secret.description or 'Sans description'}")
    
    print(f"\n⏱️  Mis à jour à: {asyncio.get_event_loop().time()}")

# Lancer le dashboard
asyncio.run(dashboard())
```

---

## 🚨 Gestion d'erreurs

### Erreurs courantes

```python
import sharokey

async def handle_errors():
    client = sharokey.SharokeyClient(token="votre-token")
    
    try:
        # Tentative de création avec paramètres invalides
        await client.create("", -1, 0)
        
    except sharokey.ValidationError as e:
        print(f"❌ Erreur de validation: {e}")
        # Exemple: "Content is required and must be non-empty"
        
    except sharokey.AuthenticationError as e:
        print(f"❌ Erreur d'authentification: {e}")
        # Token invalide ou expiré
        
    except sharokey.NotFoundError as e:
        print(f"❌ Secret non trouvé: {e}")
        # Secret n'existe pas ou a expiré
        
    except sharokey.AttachmentError as e:
        print(f"❌ Erreur fichier: {e}")
        # Fichier trop gros, introuvable, etc.
        
    except sharokey.NetworkError as e:
        print(f"❌ Erreur réseau: {e}")
        # Timeout, rate limiting, etc.
        
    except sharokey.SharokeyError as e:
        print(f"❌ Erreur générale: {e}")
        # Toutes autres erreurs API
```

### Validation locale

```python
# Le SDK valide automatiquement :
# - Contenu non vide
# - Heures entre 1 et 8760  
# - Vues entre 1 et 1000
# - Token configuré
# - Attachments : max 10 fichiers, 10MB total
# - OTP : email et phone mutuellement exclusifs

try:
    await client.create("", -1, 0)  # Plusieurs erreurs
except sharokey.ValidationError as e:
    print(e)  # "Content is required and must be non-empty"

# Erreur attachments
try:
    files = ["huge_file.zip"]  # > 10MB
    await client.create("test", 24, 1, attachments=files)
except sharokey.AttachmentError as e:
    print(e)  # "Total attachments size too large: 25.3MB. Maximum 10MB allowed"
```

---

## 🔐 Sécurité

### Chiffrement Zero Knowledge

- **Algorithmes** : AES-GCM-256 + PBKDF2 (10,000 itérations)
- **Chiffrement côté client** : Vos secrets ne quittent jamais votre machine en clair
- **Double clé** : keyA (serveur) + keyB (fragment URL)
- **Compatibilité totale** : Secrets créés par Python déchiffrables partout (CLI, web, etc.)

### Bonnes pratiques

```python
# ✅ Recommandé
secret = await client.create(
    "mot-de-passe-super-secret", 
    hours=1,        # Courte durée
    views=1,        # Une seule vue
    password="protection-additionnelle",
    otp_email="admin@secure.com"
)

# ❌ À éviter  
secret = await client.create(
    "mot-de-passe-super-secret",
    hours=8760,     # 1 an = trop long
    views=1000      # Trop de vues possibles
)
```

---

## 🆚 Comparaison avec CLI

| Fonctionnalité | CLI C# | Python SDK |
|---------------|--------|------------|
| **Configuration** | `sharokey config --token xxx` | `SharokeyClient(token='xxx')` |
| **Création** | `sharokey create "secret" --hours 24` | `client.create("secret", 24, 1)` |
| **Liste** | `sharokey list --limit 10` | `client.list(limit=10)` |
| **Détails** | `sharokey get ABC123` | `client.get('ABC123')` |
| **Suppression** | `sharokey delete ABC123` | `client.delete('ABC123')` |
| **Stats** | `sharokey stats` | `client.stats()` |
| **Pièces jointes** | `--attach file1 --attach file2` | `attachments=['file1', 'file2']` |
| **OTP Email** | `--otp-email user@domain.com` | `otp_email='user@domain.com'` |
| **OTP SMS** | `--otp-phone +33123456789` | `otp_phone='+33123456789'` |
| **Chiffrement** | ✅ Zero Knowledge | ✅ Identique |

---

## 📦 Installation développement

```bash
# Cloner le repo
git clone https://github.com/sharokey/python-sdk.git
cd python-sdk

# Installer en mode développement
pip install -e .[dev]

# Lancer les tests
pytest

# Linting
black sharokey/
isort sharokey/
mypy sharokey/
```

---

## 🐛 Support

- **Issues GitHub** : https://github.com/sharokey/python-sdk/issues
- **Documentation** : https://docs.sharokey.com/python
- **Examples** : [examples/](examples/)

---

## ⚡ Prêt à l'usage !

**Votre SDK Python Sharokey est prêt !**

1. ✅ **Installez** : `pip install sharokey`
2. ✅ **Configurez** : `client = SharokeyClient(token='...')`
3. ✅ **Utilisez** : API cohérente avec le CLI !

*Python SDK 1.0.0 - Compatible avec Sharokey API*