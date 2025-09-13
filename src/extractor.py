import yt_dlp
import re
from typing import Dict, Optional


class YouTubeExtractor:
    def __init__(self):
        self.ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
    
    def is_valid_youtube_url(self, url: str) -> bool:
        """Check if the URL is a valid YouTube URL"""
        youtube_patterns = [
            r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)',
            r'(https?://)?(www\.)?youtube\.com/watch\?.*v=',
        ]
        
        for pattern in youtube_patterns:
            if re.search(pattern, url):
                return True
        return False
    
    def extract_audio_info(self, url: str) -> Optional[Dict]:
        """Extract audio stream URL and metadata from YouTube video"""
        try:
            if not self.is_valid_youtube_url(url):
                raise ValueError("Invalid YouTube URL")
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'stream_url': info.get('url'),
                    'title': info.get('title', 'Unknown'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail'),
                }
                
        except Exception as e:
            print(f"Error extracting audio info: {str(e)}")
            return None
    
    def get_available_qualities(self, url: str) -> list:
        """Get available audio qualities for the video"""
        try:
            ydl_opts_quality = {
                'listformats': True,
                'quiet': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts_quality) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                
                audio_formats = [
                    f for f in formats 
                    if f.get('acodec') != 'none' and f.get('vcodec') == 'none'
                ]
                
                return audio_formats
                
        except Exception as e:
            print(f"Error getting qualities: {str(e)}")
            return []
