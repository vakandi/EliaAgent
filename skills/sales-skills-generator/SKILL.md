# Sales Skills Generator Skill

## Description
Ce skill génère automatiquement des compétences de vente complètes et prêtes à l'emploi à partir des analyses YouTube. Il transforme les données marketing brutes en skills OpenClaw structurés avec exercices, métriques et parcours d'apprentissage.

## Fonctionnalités
- 🎯 **Génération automatique de skills** - Conversion d'analyses en compétences structurées
- 📊 **Scoring de difficulté** - Niveaux adaptés (Débutant/Intermédiaire/Avancé)
- 🎓 **Parcours d'apprentissage** - Objectifs clairs, exercices, métriques
- 🔧 **Skills OpenClaw prêts** - Format compatible avec OpenClaw
- 📈 **Optimisation performance** - Basé sur les meilleures pratiques de vente
- 🔄 **Batch processing** - Génération de plusieurs skills en une fois

## Configuration requise
- Python 3.8+
- Dépendances: pandas, jinja2, markdown, pdfkit
- Fichier d'entrée: analyse JSON du YouTube Content Analyzer

## Installation
```bash
cd "C:\Users\your-username\Documents\projects\WatsonIA\skills\sales-skills-generator"
pip install -r requirements.txt
python setup.py install
```

## Utilisation
```bash
# Générer un skill à partir d'une analyse
python generator.py --input "analysis.json" --output "generated_skills/"

# Générer plusieurs skills à partir d'une playlist
python generator.py --input "batch_analysis/" --batch --output "sales_skills/"

# Générer un skill avec un niveau de difficulté spécifique
python generator.py --input "analysis.json" --difficulty "advanced" --output "advanced_skills/"

# Exporter en format OpenClaw
python generator.py --input "analysis.json" --format "openclaw" --output "openclaw_skills/"
```

## Architecture interne

### Modules principaux
1. **skill_template.py** - Modèles de skills prédéfinis
2. **difficulty_analyzer.py** - Analyse et scoring de difficulté
3. **learning_path_generator.py** - Création de parcours d'apprentissage
4. **exercise_generator.py** - Génération d'exercices pratiques
5. **metrics_calculator.py** - Calcul des métriques de succès
6. **openclaw_formatter.py** - Formatage pour OpenClaw
7. **batch_processor.py** - Traitement par lots

### Pipeline de génération
```
Input (YouTube Analysis JSON)
    ↓
Difficulty Assessment & Scoring
    ↓
Skill Structure Definition
    ↓
Learning Path Generation
    ↓
Exercise Creation
    ↓
Metrics Definition
    ↓
OpenClaw Formatting
    ↓
Export (Multiple Formats)
```

## Formats de sortie

### Skill OpenClaw JSON
```json
{
  "skill_metadata": {
    "skill_name": "Alex Hormozi - Advanced Objection Handling",
    "category": "Sales",
    "subcategory": "Objection Handling",
    "difficulty": "Advanced",
    "estimated_time": "8-10 hours",
    "created_by": "YouTube Content Analyzer + Sales Skills Generator",
    "version": "1.0.0",
    "tags": ["objection", "handling", "b2b", "negotiation"]
  },
  "learning_objectives": [
    "Master 15+ objection handling frameworks",
    "Develop response patterns for B2B objections",
    "Improve closing rate by 40%",
    "Handle price objections with confidence"
  ],
  "learning_path": {
    "phase_1": {
      "title": "Foundation",
      "duration": "2-3 hours",
      "modules": [
        {
          "name": "Understanding Objections",
          "content": "Psychology behind objections",
          "exercises": ["Obection analysis worksheet"]
        }
      ]
    },
    "phase_2": {
      "title": "Framework Mastery",
      "duration": "3-4 hours", 
      "modules": [
        {
          "name": "SPIN Method for Objections",
          "content": "Situation-Problem-Implication-Need-Payoff",
          "exercises": ["Role-play scenarios", "Case studies"]
        }
      ]
    },
    "phase_3": {
      "title": "Advanced Application",
      "duration": "3-4 hours",
      "modules": [
        {
          "name": "Complex Objections",
          "content": "Multiple objections, timing objections",
          "exercises": ["Real-world simulations", "Performance tracking"]
        }
      ]
    }
  },
  "practice_exercises": [
    {
      "exercise_name": "Price Objection Role-Play",
      "description": "Practice handling price objections in realistic scenarios",
      "setup": "Cold call simulation with prospect expressing budget concerns",
      "steps": [
        "Identify the real objection behind price",
        "Demonstrate value through ROI",
        "Offer payment options",
        "Create urgency"
      ],
      "duration": "30 minutes",
      "difficulty": "Intermediate",
      "materials": ["Role-play script", "Value calculator", "Objection tracker"]
    },
    {
      "exercise_name": "Competition Pushback",
      "description": "Handle prospects who mention competitors",
      "setup": "Prospect mentions competitor as primary option",
      "steps": [
        "Acknowledge competitor without bashing",
        "Ask about specific concerns",
        "Differentiate on key strengths",
        "Reframe the conversation"
      ],
      "duration": "25 minutes",
      "difficulty": "Advanced",
      "materials": ["Competitor analysis template", "Differentiation matrix"]
    }
  ],
  "success_metrics": [
    {
      "metric_name": "Objection Response Time",
      "target": "< 30 seconds",
      "measurement": "Average response time to objections",
      "benchmark": "Industry average: 45 seconds"
    },
    {
      "metric_name": "Closing Rate Improvement",
      "target": "+40%",
      "measurement": "Increase in successful closes after training",
      "benchmark": "Typical improvement: 15-25%"
    },
    {
      "metric_name": "Objection Handling Success",
      "target": "> 85% resolution rate",
      "measurement": "Percentage of objections successfully resolved",
      "benchmark": "Average success rate: 60%"
    }
  ],
  "prerequisites": [
    "Basic sales knowledge",
    "Product/service understanding",
    "Communication fundamentals"
  ],
  "advanced_materials": [
    {
      "title": "Objection Handler's Playbook",
      "type": "PDF Guide",
      "description": "Comprehensive guide to 50+ objection types"
    },
    {
      "title": "Video Library",
      "type": "Video Collection",
      "description": "Real-world examples and demonstrations"
    },
    {
      "title": "Performance Tracker",
      "type": "Excel Template",
      "description": "Track progress and measure improvement"
    }
  ],
  "instructor_notes": {
    "key_teaching_points": [
      "Focus on understanding the real objection",
      "Always demonstrate value before addressing price",
      "Use specific examples and case studies",
      "Practice with real scenarios"
    ],
    "common_challenges": [
      "Rushing responses",
      "Taking objections personally",
      "Focusing on features over value"
    ],
    "tips_for_success": [
      "Record practice sessions for review",
      "Get feedback from peers",
      "Track metrics consistently",
      "Update playbook regularly"
    ]
  }
}
```

### Rapport de génération
```json
{
  "generation_report": {
    "input_analysis": "hormozi_analysis.json",
    "timestamp": "2026-02-06T20:30:00Z",
    "skills_generated": 1,
    "total_processing_time": "2m 34s",
    "difficulty_distribution": {
      "beginner": 0,
      "intermediate": 0,
      "advanced": 1
    },
    "categories_covered": ["Objection Handling", "Closing Techniques"],
    "quality_score": 92.5,
    "recommendations": [
      "Add more beginner exercises",
      "Include video demonstrations",
      "Create assessment quiz"
    ]
  }
}
```

## Configuration

### config.json
```json
{
  "skill_templates": {
    "objection_handling": {
      "difficulty_levels": {
        "beginner": {
          "estimated_time": "3-4 hours",
          "exercises_count": 5,
          "complexity": "Basic objections"
        },
        "intermediate": {
          "estimated_time": "5-6 hours",
          "exercises_count": 8,
          "complexity": "Common B2B objections"
        },
        "advanced": {
          "estimated_time": "8-10 hours",
          "exercises_count": 12,
          "complexity": "Complex, multi-layered objections"
        }
      }
    },
    "closing_techniques": {
      "difficulty_levels": {
        "beginner": {
          "estimated_time": "2-3 hours",
          "exercises_count": 4
        },
        "intermediate": {
          "estimated_time": "4-5 hours", 
          "exercises_count": 7
        },
        "advanced": {
          "estimated_time": "6-8 hours",
          "exercises_count": 10
        }
      }
    }
  },
  "learning_path_settings": {
    "phases": {
      "foundation": {
        "title": "Foundation",
        "weight": 0.25,
        "focus": "Understanding concepts"
      },
      "practice": {
        "title": "Practice", 
        "weight": 0.5,
        "focus": "Hands-on application"
      },
      "mastery": {
        "title": "Mastery",
        "weight": 0.25,
        "focus": "Real-world application"
      }
    }
  },
  "export_settings": {
    "formats": ["json", "openclaw", "markdown", "pdf"],
    "include_metadata": true,
    "generate_assessments": true,
    "create_worksheets": true
  }
}
```

### Dépendances

### requirements.txt
```
pandas==2.1.0
jinja2==3.1.2
markdown==3.5.1
pdfkit==1.28.0
openpyxl==3.1.2
PyYAML==6.0.1
matplotlib==3.7.2
seaborn==0.12.2
```

## Exemples d'utilisation

### 1. Générer un skill à partir d'analyse YouTube
```bash
python generator.py --input "hormozi_analysis.json" --output "generated_skills/"
```

### 2. Générer une collection de skills
```bash
python generator.py --input "batch_analyses/" --batch --output "sales_skills_collection/"
```

### 3. Exporter pour OpenClaw
```bash
python generator.py --input "analysis.json" --format "openclaw" --output "openclaw_library/"
```

## Intégration avec d'autres skills

- **YouTube Content Analyzer** → Fournit les analyses marketing
- **YouTube Transcription Skill** → Fournit les transcriptions brutes
- **OpenClaw** → Utilise les skills générés pour l'entraînement

## Monitoring & Qualité

- **Scoring automatique** des skills générés
- **Recommandations d'amélioration** basées sur best practices
- **Validation du contenu** contre des standards de qualité
- **Metrics de performance** de génération

---

**Créé par Mycroft IA**  
**Version: 1.0.0**  
**Date: 2026-02-06**