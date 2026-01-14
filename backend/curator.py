import json
import random
import datetime
import os
import urllib.request
import urllib.error
import marketer

# --- CONFIG ---
LIBRARY_PATH = 'master_library.json'
OUTPUT_PATH = '../js/data.js'
GNEWS_API_KEY = os.environ.get('GNEWS_API_KEY')

# --- 1. THE PULSE ENGINE (Real + Simulated) ---

GENRES = {
    "Conflict": ["war", "chaos", "politics", "survival", "history"],
    "Tech/Future": ["technology", "future", "nature", "science", "dune"],
    "Romance/Melancholy": ["love", "romance", "memory", "nostalgia", "heartbreak"],
    "Spiritual/Deep": ["spirituality", "meditation", "divine", "gratitude", "poetry"],
    "Social/Justice": ["class", "inequality", "society", "justice", "truth"]
}

def analyze_mood(news_headline):
    """
    Very simple keyword matching to simulate LLM sentiment analysis.
    """
    news_lower = news_headline.lower()
    
    # Simple Heuristic
    if any(x in news_lower for x in ["war", "attack", "crisis", "tension", "army"]):
        return "Conflict"
    elif any(x in news_lower for x in ["ai", "tech", "space", "launch", "robot", "climate"]):
        return "Tech/Future"
    elif any(x in news_lower for x in ["love", "marriage", "divorce", "valentine", "heart"]):
        return "Romance/Melancholy"
    elif any(x in news_lower for x in ["protest", "strike", "law", "court", "scandal"]):
        return "Social/Justice"
    else:
        return "Spiritual/Deep" # Default fall back to deep art

def fetch_real_news():
    """Fetches top headlines from GNews API."""
    if not GNEWS_API_KEY:
        return None
        
    url = f"https://gnews.io/api/v4/top-headlines?category=general&lang=en&max=5&apikey={GNEWS_API_KEY}"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.load(response)
            if data.get('articles'):
                # Return a random headline from the top 5
                return random.choice(data['articles'])['title']
    except Exception as e:
        print(f"Warning: News API failed ({e}). Falling back to simulation.")
        return None
    return None

def get_simulated_headline():
    """Fallback simulation if API is down or no key provided."""
    topics = [
        "Massive AI breakthrough changes how we write code", 
        "Tensions rise in the border regions as peace talks fail",
        "A quiet day of reflection and meditation across the globe",
        "Protests erupt over wealth inequality in major capitals"
    ]
    return random.choice(topics)

# --- 2. THE CURATOR ---

import re

def get_previous_ids(output_path):
    """Parses existing data.js to find IDs currently displayed."""
    ids = set()
    try:
        with open(output_path, 'r') as f:
            content = f.read()
            matches = re.findall(r'id:\s*"([^"]+)"', content)
            ids.update(matches)
    except FileNotFoundError:
        pass
    return ids

def load_library():
    with open(LIBRARY_PATH, 'r') as f:
        return json.load(f)

def score_item(item, mood_tags):
    """Score an item based on tag overlap with mood."""
    score = 0
    for tag in item['tags']:
        if tag in mood_tags:
            score += 2
    return score

def select_daily_edition(library, mood, excluded_ids):
    """Selects 5 items per category based on mood, prioritizing fresh items."""
    mood_tags = GENRES[mood]
    edition = {}
    
    for category in ['movies', 'music', 'books']:
        items = library[category]
        random.shuffle(items) # Base randomness
        
        # Separate into fresh and stale
        fresh = [x for x in items if x['id'] not in excluded_ids]
        stale = [x for x in items if x['id'] in excluded_ids]
        
        # Sort both by mood score
        fresh.sort(key=lambda x: score_item(x, mood_tags), reverse=True)
        stale.sort(key=lambda x: score_item(x, mood_tags), reverse=True)
        
        # Prioritize fresh items
        final_pool = fresh + stale
        selected = final_pool[:5]
        
        # Apply layout logic
        layouts = ['featured', 'tall', 'wide', 'regular', 'regular']
        for i, item in enumerate(selected):
            item['layout'] = layouts[i]
            item['dailyContext'] = item['defaultContext']
            
        edition[category] = selected
        
    return edition

# --- 3. THE GENERATOR ---

def generate_js(edition):
    js_content = "const recommendations = {\n"
    
    for category, items in edition.items():
        js_content += f"    {category}: [\n"
        for item in items:
            js_content += "        {\n"
            for key, value in item.items():
                if key == "tags" or key == "defaultContext": continue
                if isinstance(value, str):
                    clean_val = value.replace('"', '\\"')
                    js_content += f'            {key}: "{clean_val}",\n'
                else:
                    js_content += f'            {key}: {value},\n'
            js_content += "        },\n"
        js_content += "    ],\n"
    
    js_content += "};\n"
    return js_content

# --- MAIN LOOP ---

if __name__ == "__main__":
    print("--- ANIMA WORLD PULSE AGENT v2.0 ---")
    
    # 1. Input (Real vs Simulated)
    headline = fetch_real_news()
    if headline:
        print("Connected to Global Neural Link (GNews)...")
    else:
        print("Neural Link Offline. Simulating inputs...")
        headline = get_simulated_headline()
        
    print(f"HEADLINE DETECTED: '{headline}'")
    
    # 2. Analyze
    mood = analyze_mood(headline)
    print(f"DETECTED MOOD: {mood}")
    
    # 3. Curate
    previous_ids = get_previous_ids(OUTPUT_PATH)
    print(f"Avoiding {len(previous_ids)} recently shown items.")
    
    lib = load_library()
    edition = select_daily_edition(lib, mood, previous_ids)
    print("Curation Complete. Updating Frontend...")
    
    # 4. Generate
    js = generate_js(edition)
    with open(OUTPUT_PATH, 'w') as f:
        f.write(js)
        
    print(f"Successfully updated {OUTPUT_PATH}")

    # 5. Hype Agent (Marketing)
    try:
        marketer.run_marketing_campaign(edition, mood, headline)
    except Exception as e:
        print(f"Marketing Agent failed (non-critical): {e}")
