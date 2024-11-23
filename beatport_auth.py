import requests

class BeatportAuth:
    # Base URLs
    AUTH_URL = "https://account.beatport.com"
    API_BASE = "https://api.beatport.com/v4/"
    
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.token_expires = None
        self.session = requests.Session()
        
    def get_auth_headers(self):
        return {
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive",
            "User-Agent": "okhttp/4.12.0",
            "Authorization": f"Bearer {self.access_token}" if self.access_token else None
        }
        
    def get_stream_url(self, track_id):
        """Get streaming URL for a track"""
        url = f"{self.API_BASE}catalog/tracks/{track_id}/stream/"
        response = self.session.get(
            url,
            headers=self.get_auth_headers()
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get stream URL: {response.text}")
            
        data = response.json()
        return data