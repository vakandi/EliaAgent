# YouTube Transcription Skill

## Description
Ce skill permet de télécharger et transcrire automatiquement les vidéos YouTube pour créer des compétences de vente basées sur le contenu d'Alex Hormozi.

## Fonctionnalités
- Téléchargement de vidéos YouTube
- Transcription automatique
- Extraction de concepts de vente
- Création de skills structurés
- Support de plusieurs providers AI

## Configuration requise
- Python 3.8+
- yt-dlp (pour le téléchargement)
- OpenAI API key (pour la transcription)
- Fichier de configuration API

## Installation
```bash
# Installer les dépendances
pip install yt-dlp openai-whisper youtube-transcript-api requests

# Configurer les API keys
cp config.example.json config.json
# Éditer config.json avec vos clés API
```

## Utilisation
```bash
# Transcrire une vidéo YouTube
python main.py --url "https://youtube.com/watch?v=VIDEO_ID"

# Transcrire une playlist
python main.py --playlist "PLAYLIST_URL" --batch

# Créer un skill à partir de la transcription
python main.py --url "VIDEO_URL" --create-skill --output "sales-skill.json"
```

## Structure de sortie
```json
{
  "title": "Titre de la vidéo",
  "transcription": "Texte transcrit complet",
  "key_concepts": [
    {
      "concept": "Nom du concept",
      "description": "Explication",
      "examples": ["Exemple 1", "Exemple 2"],
      "skill_level": "Débutant/Intermédiaire/Avancé"
    }
  ],
  "sales_frameworks": [
    {
      "name": "Nom du framework",
      "steps": ["Étape 1", "Étape 2"],
      "key_takeaways": ["Point 1", "Point 2"]
    }
  ],
  "actionable_skills": [
    {
      "skill_name": "Nom de la compétence",
      "description": "Description",
      "practice_exercise": "Exercice d'application",
      "metrics": "Comment mesurer le succès"
    }
  ]
}
```

## Exemples d'utilisation
1. **Analyser une vidéo de vente d'Alex Hormozi**
2. **Extraire les frameworks de vente utilisés**
3. **Créer des compétences pratiques pour les vendeurs**
4. **Générer du contenu éducatif structuré**

## Dépendances
- yt-dlp: Téléchargement de vidéos
- openai-whisper: Transcription haute qualité
- youtube-transcript-api: Alternative pour les transcriptions
- requests: Gestion des API
- json: Structuration des données