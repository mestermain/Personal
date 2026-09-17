import re

def convert_gdrive_url(url):
    """
    Transforms any shareable Google Drive link into a direct CDN image link.
    Supports formats:
    - https://drive.google.com/file/d/FILE_ID/view?usp=sharing
    - https://drive.google.com/open?id=FILE_ID
    - https://drive.google.com/uc?id=FILE_ID
    - https://docs.google.com/uc?id=FILE_ID
    Returns: https://lh3.googleusercontent.com/d/FILE_ID
    """
    if not url or not isinstance(url, str):
        return url
    url = url.strip()
    
    # Format 1: /file/d/FILE_ID
    match_file = re.search(r'drive\.google\.com/file/d/([a-zA-Z0-9_-]+)', url)
    if match_file:
        file_id = match_file.group(1)
        return f"https://lh3.googleusercontent.com/d/{file_id}"
    
    # Format 2: ?id=FILE_ID or &id=FILE_ID
    match_id = re.search(r'drive\.google\.com/.*[?&]id=([a-zA-Z0-9_-]+)', url)
    if match_id:
        file_id = match_id.group(1)
        return f"https://lh3.googleusercontent.com/d/{file_id}"

    # Format 3: docs.google.com
    match_docs = re.search(r'docs\.google\.com/.*[?&]id=([a-zA-Z0-9_-]+)', url)
    if match_docs:
        file_id = match_docs.group(1)
        return f"https://lh3.googleusercontent.com/d/{file_id}"

    return url
