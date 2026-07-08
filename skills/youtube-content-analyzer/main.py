#!/usr/bin/env python3
"""
Main script for YouTube Content Analyzer
========================================

Analyse les vidéos YouTube pour extraire des données marketing et vente.
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
    from analyzer import YouTubeContentAnalyzer
except ImportError:
    print("Erreur: Le module analyzer.py n'existe pas. Veuillez créer le fichier analyzer.py.")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="YouTube Content Analyzer - Analyse marketing et vente des vidéos YouTube")
    
    # Arguments principaux
    parser.add_argument('--url', type=str, help="URL de la vidéo YouTube à analyser")
    parser.add_argument('--playlist', type=str, help="URL de la playlist YouTube à analyser")
    parser.add_argument('--input', type=str, help="Fichier d'entrée (transcription JSON)")
    parser.add_argument('--output', type=str, required=True, help="Fichier de sortie pour l'analyse")
    
    # Options de traitement
    parser.add_argument('--batch', action='store_true', help="Activer le traitement par lots")
    parser.add_argument('--create-analysis', action='store_true', help="Créer une analyse complète")
    parser.add_argument('--generate-skills', action='store_true', help="Générer des skills à partir de l'analyse")
    parser.add_argument('--difficulty', type=str, choices=['beginner', 'intermediate', 'advanced'], 
                       help="Niveau de difficulté pour la génération de skills")
    
    # Options de format
    parser.add_argument('--format', type=str, choices=['json', 'markdown', 'pdf'], 
                       default='json', help="Format de sortie")
    
    # Options de debug
    parser.add_argument('--debug', action='store_true', help="Mode debug avec logs détaillés")
    parser.add_argument('--verbose', action='store_true', help="Mode verbose")
    
    args = parser.parse_args()
    
    # Valider les arguments
    if not args.url and not args.playlist and not args.input:
        print("Erreur: Vous devez spécifier --url, --playlist ou --input")
        parser.print_help()
        sys.exit(1)
    
    # Créer l'analyseur
    try:
        analyzer = YouTubeContentAnalyzer(debug=args.debug)
        
        if args.debug:
            print("=== YouTube Content Analyzer Initialisé ===")
            print(f"Mode debug: {args.debug}")
            print(f"Mode verbose: {args.verbose}")
        
        # Traiter la vidéo unique
        if args.url:
            if args.debug:
                print(f"\nAnalyse de la vidéo: {args.url}")
            
            if args.create_analysis:
                # Téléchargement + transcription + analyse
                result = analyzer.analyze_video_with_transcription(args.url)
            else:
                # Analyse à partir d'une transcription existante
                result = analyzer.analyze_video(args.url)
            
            # Sauvegarder le résultat
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Analyse sauvegardée dans: {args.output}")
            
            # Générer des skills si demandé
            if args.generate_skills:
                skills = analyzer.generate_skills(result, difficulty=args.difficulty)
                skills_output = args.output.replace('.json', '_skills.json')
                
                with open(skills_output, 'w', encoding='utf-8') as f:
                    json.dump(skills, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Skills générés dans: {skills_output}")
        
        # Traiter la playlist
        elif args.playlist:
            if args.debug:
                print(f"\nAnalyse de la playlist: {args.playlist}")
            
            if args.batch:
                # Traiter toute la playlist
                results = analyzer.analyze_playlist(args.playlist)
                
                # Sauvegarder chaque analyse
                output_dir = Path(args.output)
                output_dir.mkdir(exist_ok=True)
                
                for i, result in enumerate(results):
                    video_output = output_dir / f"video_{i+1:03d}_analysis.json"
                    with open(video_output, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                    
                    print(f"✅ Analyse {i+1} sauvegardée dans: {video_output}")
                
                # Générer un rapport consolidé
                consolidated_report = analyzer.consolidate_playlist_analysis(results)
                report_output = output_dir / "consolidated_analysis.json"
                
                with open(report_output, 'w', encoding='utf-8') as f:
                    json.dump(consolidated_report, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Rapport consolidé sauvegardé dans: {report_output}")
            
            else:
                # Traiter une seule vidéo de la playlist
                result = analyzer.analyze_playlist_video(args.playlist)
                
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Analyse sauvegardée dans: {args.output}")
        
        # Traiter un fichier d'entrée
        elif args.input:
            if args.debug:
                print(f"\nAnalyse du fichier d'entrée: {args.input}")
            
            # Charger le fichier d'entrée
            with open(args.input, 'r', encoding='utf-8') as f:
                input_data = json.load(f)
            
            # Analyser les données
            result = analyzer.analyze_transcription(input_data)
            
            # Sauvegarder le résultat
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Analyse sauvegardée dans: {args.output}")
        
        # Générer un rapport
        if args.format != 'json':
            analyzer.generate_report(args.output, args.format)
            print(f"✅ Rapport généré au format {args.format.upper()}")
        
        print("\n=== Analyse terminée avec succès! ===")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()