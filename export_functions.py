
import unicodedata

def slugify(name):
    """Convert 'Turkey Taco Skillet' to 'turkey-taco-skillet'."""
    # Normalize accents: "é" → "e"
    name = unicodedata.normalize('NFKD', name)
    name = "".join(ch for ch in name if not unicodedata.combining(ch))
    
    # Lowercase and trim
    name = name.lower().strip()
    
    # Spaces → hyphens
    name = name.replace(' ', '-')
    
    # Remove non-alphanumeric (except hyphens)
    name = "".join(ch for ch in name if ch.isalnum() or ch == '-')
    
    # Collapse multiple hyphens
    while '--' in name:
        name = name.replace('--', '-')
    
    # Trim leading/trailing hyphens
    name = name.strip('-')
    
    # Fallback
    return name or "recipe"