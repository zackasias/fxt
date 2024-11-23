import requests
import m3u8
from Crypto.Cipher import AES
import os
from urllib.parse import urljoin, urlparse
import logging
import ffmpeg

class BeatportStream:
    def __init__(self, auth):
        self.auth = auth
        self.session = requests.Session()
        self.base_url = None
        
        # Use the same logger and debug setting as BeatportApi
        self.debug_log = logging.getLogger('beatport_debug')
        self.debug_enabled = auth.debug_enabled
        
    def get_stream_manifest(self, stream_url):
        """Fetch and parse HLS manifest"""
        headers = {
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13; sdk_gphone64_arm64 Build/TE1A.240213.009)",
            "Authorization": f"Bearer {self.auth.access_token}"
        }
        
        if self.debug_enabled:
            self.debug_log.debug(f"Fetching manifest from: {stream_url}")
            self.debug_log.debug(f"Headers: {headers}")
        
        response = self.session.get(stream_url, headers=headers)
        
        if self.debug_enabled:
            self.debug_log.debug(f"Response status: {response.status_code}")
            self.debug_log.debug(f"Response headers: {dict(response.headers)}")
            self.debug_log.debug(f"Response body: {response.text[:1000]}...")
        
        if response.status_code != 200:
            raise Exception(f"Failed to get manifest: {response.text}")
            
        manifest = m3u8.loads(response.text)
        
        # Store base URL for later use with relative paths
        parsed_url = urlparse(stream_url)
        self.base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path.rsplit('/', 1)[0]}/"
        
        # Get key URL
        key_url = None
        if manifest.keys and manifest.keys[0].uri:
            key_url = urljoin(self.base_url, manifest.keys[0].uri)
            if self.debug_enabled:
                self.debug_log.debug(f"Key URL: {key_url}")
            
        return {
            'manifest': manifest,
            'key_url': key_url,
            'segments': manifest.segments
        }
        
    def get_encryption_key(self, key_url):
        """Fetch AES-128 encryption key"""
        headers = {
            "Accept-Encoding": "gzip", 
            "Connection": "Keep-Alive",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13; sdk_gphone64_arm64 Build/TE1A.240213.009)"
        }
        
        if self.debug_enabled:
            self.debug_log.debug(f"Fetching encryption key from: {key_url}")
            self.debug_log.debug(f"Headers: {headers}")
        
        response = self.session.get(key_url, headers=headers)
        
        if self.debug_enabled:
            self.debug_log.debug(f"Response status: {response.status_code}")
            self.debug_log.debug(f"Response headers: {dict(response.headers)}")
        
        if response.status_code != 200:
            raise Exception(f"Failed to get encryption key: {response.text}")
            
        return response.content
        
    def download_segments(self, manifest_data, output_file):
        """Download and decrypt HLS segments"""
        try:
            key = None
            if manifest_data['key_url']:
                key = self.get_encryption_key(manifest_data['key_url'])
                
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
            
            # Create temporary file for raw AAC data
            temp_aac = output_file + '.temp.aac'
            
            try:
                with open(temp_aac, 'wb') as outfile:
                    for segment in manifest_data['segments']:
                        # Get full segment URL
                        segment_url = urljoin(self.base_url, segment.uri)
                        
                        # Download segment
                        response = self.session.get(segment_url)
                        if response.status_code != 200:
                            raise Exception(f"Failed to download segment: {response.text}")
                            
                        data = response.content
                        
                        # Decrypt if needed
                        if key:
                            iv = bytes.fromhex(segment.key.iv[2:] if segment.key.iv else '0' * 32)
                            cipher = AES.new(key, AES.MODE_CBC, iv)
                            data = cipher.decrypt(data)
                        
                        # Write segment data
                        outfile.write(data)

                # Convert raw AAC to M4A using ffmpeg
                stream = (
                    ffmpeg
                    .input(temp_aac)
                    .output(
                        output_file,
                        acodec='copy',
                        f='ipod',
                        brand='M4A ',
                        movflags='+faststart'
                    )
                )
                ffmpeg.run(stream, capture_stdout=True, capture_stderr=True, overwrite_output=True)
                
            finally:
                # Clean up temporary AAC file
                if os.path.exists(temp_aac):
                    os.remove(temp_aac)
            
        except Exception as e:
            # Clean up failed download
            if os.path.exists(output_file):
                try:
                    os.remove(output_file)
                except:
                    pass
            raise