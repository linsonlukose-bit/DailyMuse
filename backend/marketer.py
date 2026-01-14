import datetime
import os
import re

# --- CONFIG ---
SITE_URL = "https://linsonlukose-bit.github.io/DailyMuse" # Actual user site
RSS_FILE = "../feed.xml"
HTML_FILE = "../index.html"
SOCIAL_FILE = "../daily_share.txt"

def update_seo(edition, headlines):
    """
    Injects dynamic Open Graph tags into index.html so links look fresh daily.
    """
    try:
        # 1. Construct the Description
        # e.g., "Today: Seven Samurai, Kind of Blue, and The Stranger."
        mov = edition['movies'][0]['title']
        mus = edition['music'][0]['title']
        bk = edition['books'][0]['title']
        
        # Get the first image as the preview card
        # Note: Github Pages needs absolute URL for OG Image
        img_rel = edition['movies'][0]['image']
        img_abs = f"{SITE_URL}/{img_rel}"
        
        title_text = f"ANIMA | Daily Art Curation: {datetime.date.today().isoformat()}"
        desc_text = f"Today's Mood: {headlines['mood']}. Featuring {mov}, {mus}, and {bk}."
        
        with open(HTML_FILE, 'r') as f:
            html = f.read()
            
        # Regex replacement for meta tags
        # Replaces <meta property="og:title" content="...">
        html = re.sub(r'<meta property="og:title" content="[^"]+"', f'<meta property="og:title" content="{title_text}"', html)
        html = re.sub(r'<meta property="og:description" content="[^"]+"', f'<meta property="og:description" content="{desc_text}"', html)
        html = re.sub(r'<meta property="og:image" content="[^"]+"', f'<meta property="og:image" content="{img_abs}"', html)
        
        # Also twitter cards
        html = re.sub(r'<meta name="twitter:title" content="[^"]+"', f'<meta name="twitter:title" content="{title_text}"', html)
        html = re.sub(r'<meta name="twitter:description" content="[^"]+"', f'<meta name="twitter:description" content="{desc_text}"', html)
        html = re.sub(r'<meta name="twitter:image" content="[^"]+"', f'<meta name="twitter:image" content="{img_abs}"', html)

        with open(HTML_FILE, 'w') as f:
            f.write(html)
            
        print("SEO: Meta tags updated.")
            
    except Exception as e:
        print(f"SEO Error: {e}")

def update_rss(edition, headlines):
    """
    Updates the RSS XML feed with the new entry.
    """
    today = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    # Item Content
    mov = edition['movies'][0]
    mus = edition['music'][0]
    bk = edition['books'][0]
    
    item_title = f"Edition {datetime.date.today()}: {headlines['mood']}"
    item_desc = f"""
    <![CDATA[
    <h3>Todays Mood: {headlines['mood']}</h3>
    <p>Inspired by: {headlines['news']}</p>
    <hr/>
    <p><strong>Cinema:</strong> {mov['title']} ({mov['subtitle']})<br/>
    <em>"{mov['defaultContext']}"</em></p>
    <img src="{SITE_URL}/{mov['image']}" width="300"/>
    <hr/>
    <p><strong>Music:</strong> {mus['title']} ({mus['subtitle']})</p>
    <hr/>
    <p><strong>Literature:</strong> {bk['title']} ({bk['subtitle']})</p>
    <p><a href="{SITE_URL}">Visit ANIMA for the full experience.</a></p>
    ]]>
    """
    
    new_item = f"""
    <item>
        <title>{item_title}</title>
        <link>{SITE_URL}</link>
        <guid isPermaLink="false">{SITE_URL}/{datetime.date.today()}</guid>
        <pubDate>{today}</pubDate>
        <description>{item_desc.strip()}</description>
    </item>
    """
    
    try:
        # Check if feed exists, if not create header
        if not os.path.exists(RSS_FILE):
            with open(RSS_FILE, 'w') as f:
                f.write(f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
 <title>ANIMA | Daily Muse</title>
 <description>Daily curated art, music, and cinema.</description>
 <link>{SITE_URL}</link>
 <lastBuildDate>{today}</lastBuildDate>
 <pubDate>{today}</pubDate>
</channel>
</rss>""")
        
        # Insert new item after <pubDate> in channel
        # This is a bit hacky string manipulation but works for static agents
        with open(RSS_FILE, 'r') as f:
            content = f.read()
            
        # Update Build Date
        content = re.sub(r'<lastBuildDate>.*?</lastBuildDate>', f'<lastBuildDate>{today}</lastBuildDate>', content)
        
        # Inject Item
        # Find position after <channel> header stuff, or just before </channel> closing
        # We want it at the top ideally
        
        # Helper to insert after the channel header block
        # Let's just prepend to the existing items. We'll find the first <item> or </channel>
        if "<item>" in content:
            parts = content.split("<item>", 1)
            new_content = parts[0] + new_item + "<item>" + parts[1]
        else:
            parts = content.split("</channel>")
            new_content = parts[0] + new_item + "</channel>" + parts[1]
            
        with open(RSS_FILE, 'w') as f:
            f.write(new_content)
            
        print("RSS: Feed updated.")
        
    except Exception as e:
        print(f"RSS Error: {e}")

def generate_social_copy(edition, headlines):
    """
    Creates a text file with copy-paste social posts.
    """
    mov = edition['movies'][0]
    date_str = datetime.date.today().strftime("%b %d")
    
    copy = f"""
--- SOCIAL SHARE FOR {date_str} ---

[TWITTER / BLUESKY]
Today's Mood: {headlines['mood']} 🌑

Featuring:
🎥 {mov['title']} ({mov['subtitle']})
💿 {edition['music'][0]['title']}
📖 {edition['books'][0]['title']}

Curated by the ANIMA Engine.
{SITE_URL}

[REDDIT - r/TrueFilm or r/ArtHistory]
Title: Daily Art Curation: {mov['title']} and the theme of {headlines['mood']}
Body:
Today's edition of ANIMA pairs {mov['title']} with the music of {edition['music'][0].get('subtitle', 'Unknown')}.
The common thread is "{headlines['mood']}" - responding to the headline: "{headlines['news']}".
Check it out here: {SITE_URL}

---------------------------------
    """
    try:
        with open(SOCIAL_FILE, 'w') as f:
            f.write(copy)
        print("MARKETING: Social copy generated.")
    except Exception as e:
        print(f"Marketing Error: {e}")

def run_marketing_campaign(edition, mood, news_headline):
    print("--- HYPE AGENT ACTIVATED ---")
    headlines = {"mood": mood, "news": news_headline}
    
    update_seo(edition, headlines)
    update_rss(edition, headlines)
    generate_social_copy(edition, headlines)
    print("--- CAMPAIGN COMPLETE ---")
