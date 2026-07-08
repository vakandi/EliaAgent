#!/usr/bin/env python3
"""
YouTube Transcription Skill - Télécharge et transcrit des vidéos YouTube

Auteur: Mycroft IA
Version: 1.0.1
Date: 2026-02-07

Fonctionnalités:
- Téléchargement de vidéos YouTube
- Transcription automatique avec Whisper
- Sauvegarde des transcriptions brutes
"""

import argparse
import asyncio
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests
from dataclasses import dataclass
from enum import Enum

import logging

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VideoSource(Enum):
    YOUTUBE = "youtube"
    PLAYLIST = "playlist"
    VIDEO_URL = "video_url"

@dataclass
class VideoInfo:
    """Informations sur une vidéo"""
    url: str
    title: str
    description: str
    duration: int
    upload_date: str
    view_count: int
    channel: str
    video_id: str

@dataclass
class TranscriptionResult:
    """Résultat de la transcription"""
    video_info: VideoInfo
    transcription: str

class YouTubeDownloader:
    """Téléchargeur de vidéos YouTube"""
    
    def __init__(self, download_dir: str = "downloads"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
    def download_video(self, url: str) -> Tuple[str, VideoInfo]:
        """Télécharge une vidéo YouTube"""
        try:
            logger.info(f"Téléchargement de la vidéo: {url}")
            
            # Commande yt-dlp pour obtenir les métadonnées
            metadata_cmd = [
                'yt-dlp',
                '--dump-json',
                '--quiet',
                url
            ]
            
            result = subprocess.run(metadata_cmd, capture_output=True, text=True, check=True)
            metadata = json.loads(result.stdout)
            
            # Créer l'objet VideoInfo
            video_info = VideoInfo(
                url=url,
                title=metadata.get('title', 'Unknown'),
                description=metadata.get('description', ''),
                duration=metadata.get('duration', 0),
                upload_date=metadata.get('upload_date', ''),
                view_count=metadata.get('view_count', 0),
                channel=metadata.get('channel', 'Unknown'),
                video_id=metadata.get('id', '')
            )
            
            # Télécharger la vidéo
            video_path = self.download_dir / f"{video_info.video_id}.mp4"
            download_cmd = [
                'yt-dlp',
                '-f', 'best[ext=mp4]',
                '-o', str(video_path),
                '--quiet',
                url
            ]
            
            subprocess.run(download_cmd, check=True)
            
            logger.info(f"Vidéo téléchargée: {video_path}")
            return str(video_path), video_info
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Erreur lors du téléchargement: {e}")
            raise
        except Exception as e:
            logger.error(f"Erreur inattendue: {e}")
            raise

class VideoTranscriber:
    """Transcripteur de vidéos"""
    
    def __init__(self, model_name: str = "base"):
        self.model_name = model_name
        
    def transcribe_video(self, video_path: str) -> str:
        """Transcrit une vidéo en utilisant Whisper"""
        try:
            logger.info(f"Transcription de la vidéo: {video_path}")
            
            # Vérifier si la vidéo existe
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Vidéo non trouvée: {video_path}")
            
            # Commande Whisper
            cmd = [
                'whisper',
                video_path,
                '--model', self.model_name,
                '--language', 'en',
                '--output_format', 'json',
                '--output_dir', 'transcriptions' # Temporaire, sera déplacé
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Lire le fichier de transcription
            transcription_path = Path('transcriptions') / f"{Path(video_path).stem}.json"
            if transcription_path.exists():
                with open(transcription_path, 'r', encoding='utf-8') as f:
                    transcription_data = json.load(f)
                return transcription_data.get('text', '')
            else:
                raise FileNotFoundError("Fichier de transcription non trouvé")
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Erreur lors de la transcription: {e}")
            raise
        except Exception as e:
            logger.error(f"Erreur inattendue: {e}")
            raise

class YouTubeTranscriptionSkill:
    """Skill principal de transcription YouTube"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config = self._load_config(config_file)
        self.downloader = YouTubeDownloader()
        self.transcriber = VideoTranscriber(self.config.get('whisper_model', 'base'))
        
    def _load_config(self, config_file: str) -> Dict:
        """Charge la configuration"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Fichier de configuration non trouvé: {config_file}")
            return {
                'whisper_model': 'base',
                'output_dir': 'transcriptions_output',
                'max_concurrent_downloads': 3
            }
    
    def process_video(self, url: str, output_path: str) -> TranscriptionResult:
        """Traite une vidéo YouTube complète et sauvegarde la transcription"""
        try:
            logger.info(f"Traitement de la vidéo: {url}")
            
            # 1. Télécharger la vidéo
            video_path, video_info = self.downloader.download_video(url)
            
            # 2. Transcrire la vidéo
            transcription = self.transcriber.transcribe_video(video_path)
            
            # 3. Sauvegarder la transcription brute
            self._save_transcription(transcription, video_info.video_id, video_info.title, output_path)
            
            # Nettoyer les fichiers temporaires
            self._cleanup_files(video_path)
            
            return TranscriptionResult(
                video_info=video_info,
                transcription=transcription
            )
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la vidéo: {e}")
            raise
    
    def _save_transcription(self, transcription: str, video_id: str, title: str, output_path: str):
        """Sauvegarde la transcription dans un fichier JSON"""
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Remplacer les caractères non valides dans le titre pour le nom de fichier
        safe_title = re.sub(r'[^a-zA-Z0-9_ -]', '', title).replace(' ', '_')[:50] # Limiter la longueur
        transcription_file_path = output_dir / f"{safe_title}_{video_id}.json"
        
        full_data = {
            "video_id": video_id,
            "title": title,
            "transcription": transcription,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(transcription_file_path, 'w', encoding='utf-8') as f:
            json.dump(full_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Transcription sauvegardée: {transcription_file_path}")
    
    def _cleanup_files(self, video_path: str):
        """Nettoie les fichiers temporaires"""
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
                logger.info(f"Fichier vidéo supprimé: {video_path}")
            
            # Supprimer aussi le fichier .json généré par whisper dans le dossier temporaire 'transcriptions'
            transcription_temp_path = Path('transcriptions') / f"{Path(video_path).stem}.json"
            if transcription_temp_path.exists():
                os.remove(transcription_temp_path)
                logger.info(f"Fichier de transcription temporaire supprimé: {transcription_temp_path}")
                
        except Exception as e:
            logger.warning(f"Erreur lors du nettoyage: {e}")

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="YouTube Transcription Skill")
    parser.add_argument('--url', required=True, help="URL de la vidéo YouTube")
    parser.add_argument('--output', required=True, help="Répertoire de sortie pour la transcription")
    parser.add_argument('--model', default='base', help="Modèle Whisper à utiliser")
    parser.add_argument('--config', default='config.json', help="Fichier de configuration")
    
    args = parser.parse_args()
    
    # Initialiser le skill
    skill = YouTubeTranscriptionSkill(args.config)
    
    # Traiter la vidéo
    try:
        result = skill.process_video(args.url, args.output)
        
        # Afficher les résultats
        print("\n" + "="*50)
        print("RÉSULTATS DE LA TRANSCRIPTION")
        print("="*50)
        print(f"Titre: {result.video_info.title}")
        print(f"Canal: {result.video_info.channel}")
        print(f"Durée: {result.video_info.duration} secondes")
        print("Transcription brute sauvegardée.")
        
        print("="*50)
        
    except Exception as e:
        logger.error(f"Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()