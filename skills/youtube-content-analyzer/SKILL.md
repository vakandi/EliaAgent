# YouTube Content Analyzer Skill

## Description
Ce skill analyse les transcriptions YouTube pour extraire des données marketing et vente complètes. Il identifie les patterns de vente, les arguments marketing, les objections courantes et les stratégies de conversion.

## Fonctionnalités
- 🎯 **Analyse marketing profonde** - Messages clés, target audience, value proposition
- 💰 **Stratégies de vente** - Techniques de closing, objection handling, upselling
- 📊 **Extraction de données** - KPIs, metrics, benchmarks
- 🧠 **NLP avancé** - Analyse sémantique, sentiment, intent
- 🔄 **Export structuré** - JSON, skills OpenClaw, rapports

## Configuration requise
- Python 3.8+
- Dépendances: NLTK, spacy, transformers, pandas
- Fichier de configuration: config.json

## Installation
```bash
cd "C:\Users\your-username\Documents\projects\WatsonIA\skills\youtube-content-analyzer"
pip install -r requirements.txt
python setup.py install
```

## Utilisation
```bash
# Analyser une transcription déjà existante
python analyzer.py --input "transcription.json" --output "analysis.json"

# Analyser une vidéo YouTube (combine avec transcription)
python analyzer.py --url "https://youtube.com/watch?v=abc123" --create-analysis

# Analyser une playlist
python analyzer.py --playlist "PLAYLIST_URL" --batch --output "batch_analysis/"

# Générer un rapport marketing
python analyzer.py --input "analysis.json" --format "report" --output "marketing_report.pdf"
```

## Architecture interne

### Modules principaux
1. **content_parser.py** - Parsing et nettoyage du contenu
2. **marketing_analyzer.py** - Analyse marketing (target, value prop, messaging)
3. **sales_analyzer.py** - Analyse vente (objections, closing, techniques)
4. **nlp_processor.py** - Traitement NLP avancé
5. **export_engine.py** - Export vers formats multiples
6. **skill_generator.py** - Crée des skills OpenClaw

### Pipeline d'analyse
```
Input (YouTube URL/Transcription)
    ↓
Content Cleaning & Normalization
    ↓
NLP Processing & Entity Recognition
    ↓
Marketing Analysis (Target, Messaging, Value Prop)
    ↓
Sales Analysis (Techniques, Objections, Frameworks)
    ↓
Data Structuring & Scoring
    ↓
Export (JSON, Skills, Reports)
```

## Formats de sortie

### Analyse marketing JSON
```json
{
  "marketing_analysis": {
    "target_audience": {
      "demographics": ["Entrepreneurs B2B", "Directeurs marketing"],
      "psychographics": ["Growth-oriented", "Data-driven"],
      "pain_points": ["Lead generation", "Conversion optimization"]
    },
    "value_proposition": {
      "primary_value": "Scaling revenue through systematic sales processes",
      "key_benefits": ["Proven frameworks", "Implementation guides", "Metrics tracking"],
      "unique_differentiators": ["Battle-tested", "Results-oriented", "Practical"]
    },
    "messaging_strategy": {
      "tone": "Direct, confident, results-focused",
      "key_phrases": ["Revenue growth", "Systematic approach", "Proven results"],
      "emotional_triggers": ["Success", "Growth", "Security"]
    }
  }
}
```

### Analyse vente JSON
```json
{
  "sales_analysis": {
    "techniques_identified": [
      {
        "name": "SPIN Selling",
        "confidence": 0.95,
        "context": "Used when discussing customer pain points",
        "effectiveness_score": 8.7
      }
    ],
    "objection_handling": {
      "common_objections": ["Price", "Timing", "Competition"],
      "response_patterns": ["Value demonstration", "Case studies", "ROI focus"],
      "success_rate": 87.5
    },
    "closing_techniques": {
      "identified_techniques": ["Assumptive close", "Summary close", "Takeaway close"],
      "usage_frequency": {"High": "Assumptive close", "Medium": "Summary close"},
      "effectiveness": {"Assumptive close": 92%, "Summary close": 78%}
    },
    "sales_frameworks": [
      {
        "name": "MEDDIC",
        "completeness": 0.85,
        "steps_used": ["Metrics", "Economic Buyer", "Decision Criteria"],
        "missing_elements": ["Decision Process"]
      }
    ]
  }
}
```

### Skills OpenClaw générés
```json
{
  "generated_skills": [
    {
      "skill_name": "Alex Hormozi - Objection Handling Mastery",
      "category": "Sales",
      "difficulty": "Advanced",
      "learning_objectives": [
        "Master 15+ objection handling patterns",
        "Develop response frameworks for common B2B objections",
        "Improve closing rate by 40%"
      ],
      "practice_exercises": [
        "Role-play exercises for price objections",
        "Case study analysis for timing objections",
        "Cold call simulations with competition pushback"
      ],
      "estimated_time": "6-8 hours",
      "prerequisites": ["Basic sales knowledge", "Product understanding"],
      "success_metrics": [
        "Reduced objection handling time by 50%",
        "Increased conversion rate from 25% to 65%",
        "Improved customer satisfaction score"
      ]
    }
  ]
}
```

## Configuration

### config.json
```json
{
  "nlp_settings": {
    "model": "en_core_web_lg",
    "sentiment_analysis": true,
    "entity_recognition": true,
    "topic_extraction": true
  },
  "marketing_analysis": {
    "target_audience_keywords": ["entrepreneur", "business", "revenue", "growth"],
    "value_proposition_indicators": ["results", "proven", "systematic", "framework"],
    "messaging_patterns": ["direct", "confident", "data-driven", "practical"]
  },
  "sales_analysis": {
    "technique_keywords": {
      "objection_handling": ["objection", "concern", "pushback", "resistance"],
      "closing": ["close", "deal", "commitment", "decision"],
      "prospecting": ["lead", "prospect", "cold", "outreach"]
    },
    "framework_detection": {
      "SPIN": ["situation", "problem", "implication", "need-payoff"],
      "MEDDIC": ["metrics", "economic buyer", "decision criteria"],
      "Challenger": ["teach", "tailor", "take control"]
    }
  },
  "export_settings": {
    "formats": ["json", "skill", "markdown", "pdf"],
    "include_original_content": true,
    "include_confidence_scores": true,
    "generate_skills": true
  }
}
```

## Dépendances

### requirements.txt
```
nltk==3.8.1
spacy==3.7.2
transformers==4.36.2
torch==2.1.0
pandas==2.1.0
numpy==1.24.3
scikit-learn==1.3.0
matplotlib==3.7.2
seaborn==0.12.2
reportlab==4.0.4
openpyxl==3.1.2
```

### Fonctionnalités avancées
- **Analyse de sentiment** par segment de la vidéo
- **Extraction d'entités** (personnes, entreprises, produits)
- **Détection de patterns conversationnels**
- **Scoring des techniques de vente**
- **Benchmark contre best practices**
- **Génération automatique de compétences**

## Exemples d'utilisation

### 1. Analyser une vidéo d'Alex Hormozi
```bash
python analyzer.py --url "https://youtube.com/watch?v=hormozi_video" \
  --create-analysis --output "hormozi_analysis.json"
```

### 2. Générer des compétences OpenClaw
```bash
python analyzer.py --input "hormozi_analysis.json" \
  --generate-skills --output "sales_skills/"
```

### 3. Créer un rapport marketing
```bash
python analyzer.py --input "hormozi_analysis.json" \
  --format "marketing_report" --output "report.pdf"
```

## Intégration avec d'autres skills

- **YouTube Transcription Skill** → Fournit les transcriptions brutes
- **Sales Skills Generator** → Consomme les analyses pour créer des skills
- **OpenClaw** → Utilise les skills générés pour l'entraînement

## Monitoring & Logs

- Logging détaillé de chaque étape d'analyse
- Rapports de confiance pour chaque détection
- Métriques de performance et temps de traitement
- Export des logs pour débogage

---

**Créé par Mycroft IA**  
**Version: 1.0.0**  
**Date: 2026-02-06**