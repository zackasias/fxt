# OrpheusDL - Beatport v2

A Beatport module for the OrpheusDL modular archival music program. This is an updated version that fixes streaming functionality and adds proper M4A container support.

## About OrpheusDL - Beatport

OrpheusDL - Beatport is a module written in Python which allows archiving from Beatport for the modular music archival program. This version implements proper HLS stream handling and AAC to M4A conversion.

## Features

- Full HLS stream support with proper decryption
- AAC to M4A conversion with correct container format
- Proper metadata tagging support
- Mobile app authentication flow
- Quality tier support (128k/256k AAC)
- Cover art downloading
- Playlist and album support

## Prerequisites

- OrpheusDL base installation
- Python 3.7+
- FFmpeg
- Required Python packages:
  - m3u8
  - pycryptodome
  - ffmpeg-python
  - requests

## Installation

1. Go to your orpheusdl/ directory and run:

```bash
git clone https://github.com/yourusername/orpheusdl-beatport.git modules/beatport
```

2. Install required packages:

```bash
pip install m3u8 pycryptodome ffmpeg-python
```

3. Execute:

```bash
python orpheus.py
```

## Usage

Download tracks using Beatport URLs:

```bash
python orpheus.py https://www.beatport.com/track/example/12345
```


Supported URL types:
- Tracks: `beatport.com/track/...`
- Albums: `beatport.com/release/...`
- Artists: `beatport.com/artist/...`
- Playlists: `beatport.com/playlist/...`

## Configuration

Configuration file location: `config/settings.json`

### Global Settings

```json
{
"general": {
"download_quality": "high"
},
"covers": {
"main_resolution": 1400
}
```

Quality options:
- `"high"`: AAC 256 kbit/s
- `"medium"`: AAC 128 kbit/s
- `"low"`: AAC 128 kbit/s

### Beatport Settings

```json
{
"username": "",
"password": ""
}
```

**Note**: Requires an active Beatport "LINK" subscription.

## Technical Details

### Authentication Flow
- Uses mobile app authentication flow
- Implements PKCE for secure token exchange
- Handles token refresh automatically

### Stream Handling
- HLS manifest parsing
- AES-128 decryption
- Proper AAC to M4A container conversion
- FFmpeg integration for container format

### File Processing
1. Downloads encrypted HLS segments
2. Decrypts segments using AES-128
3. Concatenates segments
4. Converts to proper M4A container
5. Applies metadata tags

## Credits

- Original module by @Dniel97, @glomatico and @reattin
- Complete authorization and stream handling rewritten to handle all the additional security measures implemented by Beatport. Used decrypted pcap's to analyze the complete flow and get access to the secrets needed to get the correct output by @johnneerdael
- Based on OrpheusDL framework

## License

This project is licensed under the MIT License - see the LICENSE file for details.
