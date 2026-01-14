import json
import urllib.request
import urllib.parse
import time
import re

# --- CONFIG ---
INGEST_FILE = 'ingest.txt'
OUTPUT_FILE = 'new_entries.json'

def fetch_google_books(query):
    """Search for a book using Google Books API."""
    try:
        base_url = "https://www.googleapis.com/books/v1/volumes"
        params = {"q": query, "maxResults": 1, "printType": "books"}
        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        
        with urllib.request.urlopen(url) as response:
            data = json.load(response)
            if "items" in data:
                info = data["items"][0]["volumeInfo"]
                return {
                    "title": info.get("title"),
                    "author": ", ".join(info.get("authors", ["Unknown"])),
                    "year": info.get("publishedDate", "")[:4],
                    "description": info.get("description", "No description available."),
                    "categories": info.get("categories", [])
                }
    except Exception as e:
        print(f"Error fetching book '{query}': {e}")
    return None

def fetch_itunes(query, media_type):
    """
    Search iTunes API.
    media_type: 'movie' or 'music' (mapped to 'musicAlbum' for albums)
    """
    entity = "movie" if media_type == "movies" else "album"
    try:
        base_url = "https://itunes.apple.com/search"
        params = {"term": query, "media": "music" if media_type == "music" else "movie", "entity": entity, "limit": 1}
        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        
        with urllib.request.urlopen(url) as response:
            data = json.load(response)
            if data["resultCount"] > 0:
                result = data["results"][0]
                return {
                    "title": result.get("trackName") or result.get("collectionName"),
                    "artist": result.get("artistName"),
                    "year": result.get("releaseDate", "")[:4],
                    "genre": result.get("primaryGenreName"),
                    # iTunes descriptions can be long or missing, handle carefully
                    "description": result.get("longDescription") or result.get("description") or f"A {result.get('primaryGenreName')} work by {result.get('artistName')}."
                }
    except Exception as e:
        print(f"Error fetching {media_type} '{query}': {e}")
    return None

def clean_filename(title):
    """Converts a title to a safe filename string."""
    s = title.lower()
    s = re.sub(r'[^a-z0-9]+', '_', s)
    s = s.strip('_')
    return s

def process_ingest_file():
    entries = {"movies": [], "music": [], "books": []}
    
    try:
        with open(INGEST_FILE, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"File {INGEST_FILE} not found. Please create it first.")
        return

    print(f"Processing {len(lines)} items...")
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"): continue
        
        # Detect type if specified, e.g., "book: Title"
        category = None
        query = line
        
        if ":" in line:
            parts = line.split(":", 1)
            type_prefix = parts[0].lower().strip()
            if type_prefix in ["movie", "movies"]: category = "movies"
            elif type_prefix in ["music", "album", "song"]: category = "music"
            elif type_prefix in ["book", "books"]: category = "books"
            
            if category:
                query = parts[1].strip()
        
        # If no category, try to auto-detect (hard, so maybe default to book or ask logic? 
        # For now, let's require prefixes or we'll guess).
        # Actually, let's try searching all 3 if unknown, but that's expensive.
        # Let's assume the user knows to prefix for now, or we default to 'movies' if ambiguous?
        # Better: Print a warning if no prefix.
        if not category:
            print(f"Skipping '{line}': Please specify type (e.g., 'movie: {line}')")
            continue

        print(f"Fetching metadata for [{category}]: {query}...")
        
        meta = None
        if category == "books":
            meta = fetch_google_books(query)
        else:
            meta = fetch_itunes(query, category)
            
        if meta:
            # Create the entry structure matching master_library.json
            safe_title = clean_filename(meta['title'])
            
            entry = {
                "id": f"{category[0]}_{int(time.time())}_{random.randint(100,999)}", # Unique ID
                "title": meta['title'],
                "subtitle": f"{meta.get('artist', meta.get('author'))}, {meta['year']}",
                "image": f"images/{safe_title}.png",
                "technicianReview": f"Automatically ingested. {meta['description'][:100]}...",
                "soulNote": "To be written by the curator.",
                "significance": "A masterpiece from the global archive.",
                "defaultContext": f"\"{meta['title']}\"",
                "artistFact": "To be added.",
                "tags": [meta.get('genre') or meta.get('categories', ['Classic'])[0], "global", "art"]
            }
            
            entries[category].append(entry)
            print(f"  -> Found: {meta['title']} ({meta['year']})")
        else:
            print(f"  -> Failed to find metadata for '{query}'")
            
        # Be nice to APIs
        time.sleep(0.5)

    # Output results
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(entries, f, indent=2)
    
    print(f"\nIngestion complete. Check {OUTPUT_FILE} for results.")
    print("REVIEW STEP: You must manually merge this into master_library.json and Generate the images!")

import random # Needed for ID generation

if __name__ == "__main__":
    process_ingest_file()
