#!/usr/bin/env python3
"""
Main script for Sales Skills Generator
=======================================

Génère automatiquement des compétences de vente à partir des analyses YouTube.
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Ajouter le chemin du skill
skill_path = Path(__file__).parent
sys.path.append(str(skill_path))

try:
    from generator import SalesSkillsGenerator
except ImportError:
    print("Erreur: Le module generator.py n'existe pas. Création du module de base...")
    
    # Créer un générateur de base si le module n'existe pas
    class SalesSkillsGenerator:
        def __init__(self, debug=False):
            self.debug = debug
            self.skill_templates = self.load_skill_templates()
        
        def load_skill_templates(self):
            """Charger les templates de skills"""
            return {
                "objection_handling": {
                    "beginner": {
                        "estimated_time": "3-4 heures",
                        "exercises_count": 5,
                        "modules": ["Comprendre les objections", "Réponses de base"]
                    },
                    "intermediate": {
                        "estimated_time": "5-6 heures", 
                        "exercises_count": 8,
                        "modules": ["SPIN Selling", "Techniques avancées"]
                    },
                    "advanced": {
                        "estimated_time": "8-10 heures",
                        "exercises_count": 12,
                        "modules": ["Objections complexes", "Stratégies multi-niveaux"]
                    }
                },
                "closing_techniques": {
                    "beginner": {
                        "estimated_time": "2-3 heures",
                        "exercises_count": 4,
                        "modules": ["Closing de base", "Signaux d'achat"]
                    },
                    "intermediate": {
                        "estimated_time": "4-5 heures",
                        "exercises_count": 7,
                        "modules": ["Closing assumptif", "Closing par résumé"]
                    },
                    "advanced": {
                        "estimated_time": "6-8 heures",
                        "exercises_count": 10,
                        "modules": ["Closing complexe", "Gestion des objections pendant le closing"]
                    }
                }
            }
        
        def generate_skill(self, analysis_data, difficulty="intermediate"):
            """Générer un skill à partir des données d'analyse"""
            
            skill_name = analysis_data.get("title", "Sales Skill")
            category = analysis_data.get("category", "Sales")
            
            # Déterminer le niveau de difficulté
            if difficulty not in self.skill_templates[category]:
                difficulty = "intermediate"
            
            template = self.skill_templates[category][difficulty]
            
            skill = {
                "skill_metadata": {
                    "skill_name": skill_name,
                    "category": category,
                    "subcategory": analysis_data.get("subcategory", "General"),
                    "difficulty": difficulty.capitalize(),
                    "estimated_time": template["estimated_time"],
                    "created_by": "Sales Skills Generator",
                    "version": "1.0.0",
                    "tags": analysis_data.get("tags", ["sales", "marketing"]),
                    "created_date": "2026-02-06"
                },
                "learning_objectives": analysis_data.get("learning_objectives", [
                    "Maîtriser les techniques de vente",
                    "Améliorer le taux de conversion",
                    "Gérer les objections efficacement"
                ]),
                "learning_path": {
                    "phase_1": {
                        "title": "Fondamentaux",
                        "duration": "1-2 heures",
                        "modules": template["modules"][:2]
                    },
                    "phase_2": {
                        "title": "Pratique",
                        "duration": template["estimated_time"].split("-")[0] + " heures", 
                        "modules": template["modules"][1:3]
                    }
                },
                "practice_exercises": self.generate_exercises(category, difficulty),
                "success_metrics": analysis_data.get("metrics", [
                    {
                        "metric_name": "Taux de conversion",
                        "target": "+30%",
                        "measurement": "Augmentation du taux de conversion"
                    },
                    {
                        "metric_name": "Temps de closing",
                        "target": "-25%",
                        "measurement": "Réduction du temps nécessaire pour clôturer"
                    }
                ]),
                "prerequisites": analysis_data.get("prerequisites", [
                    "Connaissances de base en vente",
                    "Compréhension du produit/service"
                ])
            }
            
            if self.debug:
                print(f"✅ Skill généré: {skill_name} ({difficulty})")
            
            return skill
        
        def generate_exercises(self, category, difficulty):
            """Générer des exercices pratiques"""
            
            exercises = []
            
            if category == "objection_handling":
                if difficulty == "beginner":
                    exercises = [
                        {
                            "exercise_name": "Reconnaître les objections courantes",
                            "description": "Identifier les types d'objections dans des conversations",
                            "duration": "15 minutes",
                            "difficulty": "Débutant"
                        },
                        {
                            "exercise_name": "Réponses de base aux objections",
                            "description": "Pratiquer des réponses standards aux objections fréquentes",
                            "duration": "20 minutes", 
                            "difficulty": "Débutant"
                        }
                    ]
                elif difficulty == "intermediate":
                    exercises = [
                        {
                            "exercise_name": "Technique SPIN Selling",
                            "description": "Appliquer la méthode SPIN pour gérer les objections",
                            "duration": "30 minutes",
                            "difficulty": "Intermédiaire"
                        },
                        {
                            "exercise_name": "Role-play de négociation",
                            "description": "Simuler des négociations avec objections complexes",
                            "duration": "45 minutes",
                            "difficulty": "Intermédiaire"
                        }
                    ]
                else:  # advanced
                    exercises = [
                        {
                            "exercise_name": "Gestion d'objections multiples",
                            "description": "Gérer plusieurs objections simultanées",
                            "duration": "60 minutes",
                            "difficulty": "Avancé"
                        },
                        {
                            "exercise_name": "Stratégies de breaking",
                            "description": "Techniques pour briser les résistances complexes",
                            "duration": "45 minutes",
                            "difficulty": "Avancé"
                        }
                    ]
            
            elif category == "closing_techniques":
                if difficulty == "beginner":
                    exercises = [
                        {
                            "exercise_name": "Identifier les signaux d'achat",
                            "description": "Reconnaître les indicateurs que le client est prêt à acheter",
                            "duration": "15 minutes",
                            "difficulty": "Débutant"
                        }
                    ]
                elif difficulty == "intermediate":
                    exercises = [
                        {
                            "exercise_name": "Closing assumptif",
                            "description": "Pratiquer la technique de closing assumptif",
                            "duration": "25 minutes",
                            "difficulty": "Intermédiaire"
                        }
                    ]
                else:  # advanced
                    exercises = [
                        {
                            "exercise_name": "Closing complexe avec objections",
                            "description": "Gérer les objections pendant le processus de closing",
                            "duration": "40 minutes",
                            "difficulty": "Avancé"
                        }
                    ]
            
            return exercises
        
        def generate_skills_from_analysis(self, analysis_file, difficulty="intermediate"):
            """Générer des skills à partir d'un fichier d'analyse"""
            
            # Charger les données d'analyse
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            # Générer le skill
            skill = self.generate_skill(analysis_data, difficulty)
            
            return skill
        
        def batch_generate(self, input_dir, output_dir, difficulty="intermediate"):
            """Générer plusieurs skills à partir d'un répertoire d'analyses"""
            
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            skills = []
            
            # Trouver tous les fichiers d'analyse
            for analysis_file in Path(input_dir).glob("*.json"):
                try:
                    skill = self.generate_skills_from_analysis(str(analysis_file), difficulty)
                    skills.append(skill)
                    
                    # Sauvegarder le skill individuel
                    skill_output = output_path / f"{analysis_file.stem}_skill.json"
                    with open(skill_output, 'w', encoding='utf-8') as f:
                        json.dump(skill, f, indent=2, ensure_ascii=False)
                    
                    print(f"✅ Skill généré: {skill_output}")
                    
                except Exception as e:
                    print(f"❌ Erreur avec {analysis_file}: {e}")
            
            # Générer un rapport consolidé
            if skills:
                consolidated_report = {
                    "generation_report": {
                        "input_directory": input_dir,
                        "output_directory": output_dir,
                        "skills_generated": len(skills),
                        "difficulty": difficulty,
                        "skills": skills
                    }
                }
                
                report_output = output_path / "consolidated_skills_report.json"
                with open(report_output, 'w', encoding='utf-8') as f:
                    json.dump(consolidated_report, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Rapport consolidé sauvegardé: {report_output}")
            
            return skills

def main():
    parser = argparse.ArgumentParser(description="Sales Skills Generator - Génère des compétences de vente à partir des analyses YouTube")
    
    # Arguments principaux
    parser.add_argument('--input', type=str, required=True, help="Fichier d'analyse JSON ou répertoire")
    parser.add_argument('--output', type=str, required=True, help="Répertoire de sortie pour les skills générés")
    
    # Options de génération
    parser.add_argument('--batch', action='store_true', help="Traiter tous les fichiers du répertoire d'entrée")
    parser.add_argument('--difficulty', type=str, choices=['beginner', 'intermediate', 'advanced'], 
                       default='intermediate', help="Niveau de difficulté des skills générés")
    
    # Options de format
    parser.add_argument('--format', type=str, choices=['json', 'openclaw', 'markdown'], 
                       default='json', help="Format de sortie")
    
    # Options de debug
    parser.add_argument('--debug', action='store_true', help="Mode debug avec logs détaillés")
    parser.add_argument('--verbose', action='store_true', help="Mode verbose")
    
    args = parser.parse_args()
    
    # Créer le générateur
    try:
        generator = SalesSkillsGenerator(debug=args.debug)
        
        if args.debug:
            print("=== Sales Skills Generator Initialisé ===")
            print(f"Mode debug: {args.debug}")
            print(f"Difficulté: {args.difficulty}")
        
        # Valider le chemin d'entrée
        input_path = Path(args.input)
        
        if not input_path.exists():
            print(f"❌ Le chemin d'entrée n'existe pas: {args.input}")
            sys.exit(1)
        
        # Créer le répertoire de sortie
        output_path = Path(args.output)
        output_path.mkdir(exist_ok=True)
        
        # Générer les skills
        if args.batch:
            # Traiter tous les fichiers du répertoire
            if not input_path.is_dir():
                print("❌ Pour le mode batch, l'entrée doit être un répertoire")
                sys.exit(1)
            
            print(f"\nGénération par lots depuis: {input_path}")
            skills = generator.batch_generate(str(input_path), str(output_path), args.difficulty)
            
            print(f"\n✅ {len(skills)} skills générés dans: {output_path}")
        
        else:
            # Traiter un seul fichier
            if not input_path.is_file():
                print("❌ Pour le mode unique, l'entrée doit être un fichier")
                sys.exit(1)
            
            print(f"\nGénération du skill depuis: {input_path}")
            
            skill = generator.generate_skills_from_analysis(str(input_path), args.difficulty)
            
            # Sauvegarder le skill
            skill_filename = input_path.stem + "_skill.json"
            skill_output = output_path / skill_filename
            
            with open(skill_output, 'w', encoding='utf-8') as f:
                json.dump(skill, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Skill généré: {skill_output}")
        
        # Générer un rapport
        if args.format != 'json':
            print(f"Format {args.format} pas encore implémenté")
        
        print("\n=== Génération terminée avec succès! ===")
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()