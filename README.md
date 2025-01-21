# YouTube Crawler

This project provides a Python-based solution for crawling data from YouTube using the YouTube Data API. It allows fetching video details from playlists, channels, or video IDs, with the ability to filter by publication date and handle large data sets efficiently.

## Features

- Fetch video details using:
  - Playlists or channel handles
  - Specific video IDs
- Filter videos by publication date
- Process data in chunks for efficient API usage
- Manage and reuse crawled video metadata to avoid duplication
- Supports multiple API tokens for extended functionality

This is a toy project. It would be better to change  youtube_crawler function to read information from config and logging into files etc. 

## Requirements

- Python 3.8 or higher
- Google API Python Client Library (`google-api-python-client`)
- Enabled YouTube Data API in Google Cloud Console

## Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:ZeynepP/youtube-crawler-api.git
   cd youtube-crawler-api
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up Google API credentials:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Create or select a project.
   - Enable the YouTube Data API.
   - Copy your token

## Usage

### Running the Script

Run the script and provide the required inputs when prompted:
```bash
python youtube_crawler.py
```

### Input Prompts
1. **Playlists or Channel Handles**:
   - Enter a comma-separated list of YouTube playlists or channel handles.
   - Leave empty if you prefer to provide video IDs instead.
2. **Video IDs**:
   - Enter a comma-separated list of video IDs if playlists are not provided.
3. **Date Range**:
   - Specify the start and end dates in `YYYY-MM-DD` format.
4. **API Tokens**:
   - Enter a comma-separated list of valid API tokens for authentication.

Example:
```
Enter comma separated playlists or handles / empty: PLabcd1234xyz,PLxyz5678abc
Enter comma separated video ids / no need if playlists provided: 
Enter start date YYYY-MM-DD: 2024-01-01
Enter end date YYYY-MM-DD: 2024-12-31
Enter comma separated tokens: token1,token2,token3
```

## File Structure

- **`youtube_crawler.py`**: Main script to execute the crawler.
- **`utils.py`**: Contains utility functions like saving crawled data and dividing chunks.
- **`client_google.py`**: Handles interactions with the YouTube Data API.
- **`write.py`**: Manages file writing operations.

## Logging

The script includes logging to:
- Track the crawling process.
- Suppress verbose logs from third-party libraries.


