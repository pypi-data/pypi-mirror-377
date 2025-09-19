"""
Fun generator gadgets.

Entertainment and utility tools for testing MCP functionality with
random generators, games, and creative utilities.
"""

import random
import uuid
import string
from typing import Dict, Any, List
from fastmcp import Context
from mcp_foundation.server.context import get_mcp
from ..utils.validate import validate_required_param

mcp = get_mcp()

# Fun data for generators
PROGRAMMING_QUOTES = [
    "The best way to debug code is to never write bugs in the first place.",
    "Code is like humor. When you have to explain it, it's bad.",
    "Programming is thinking, not typing.",
    "The most dangerous phrase in the language is 'we've always done it this way.'",
    "Software is a great combination of artistry and engineering.",
    "Clean code always looks like it was written by someone who cares.",
    "Any fool can write code that a computer can understand. Good programmers write code that humans can understand.",
    "First, solve the problem. Then, write the code.",
    "Experience is the name everyone gives to their mistakes.",
    "The only way to learn a new programming language is by writing programs in it."
]

MOTIVATIONAL_QUOTES = [
    "The way to get started is to quit talking and begin doing.",
    "Innovation distinguishes between a leader and a follower.",
    "Life is what happens when you're busy making other plans.",
    "The future belongs to those who believe in the beauty of their dreams.",
    "It is during our darkest moments that we must focus to see the light.",
    "Success is not final, failure is not fatal: it is the courage to continue that counts.",
    "The only impossible journey is the one you never begin.",
    "In the midst of winter, I found there was, within me, an invincible summer.",
    "It does not matter how slowly you go as long as you do not stop.",
    "Everything you've ever wanted is on the other side of fear."
]

FUNNY_QUOTES = [
    "I have not failed. I've just found 10,000 ways that won't work.",
    "A computer once beat me at chess, but it was no match for me at kick boxing.",
    "The problem with troubleshooting is that trouble shoots back.",
    "99 little bugs in the code, 99 little bugs. Take one down, patch it around, 117 little bugs in the code.",
    "There are only 10 types of people in the world: those who understand binary and those who don't.",
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Programming is like sex. One mistake and you have to support it for the rest of your life.",
    "A SQL query goes into a bar, walks up to two tables and asks, 'Can I join you?'",
    "How many programmers does it take to change a light bulb? None. It's a hardware problem.",
    "I would tell you a UDP joke, but you might not get it."
]

FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn",
    "Blake", "Cameron", "Dakota", "Sage", "River", "Phoenix", "Rowan", "Skyler"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas"
]

COMPANY_PREFIXES = ["Tech", "Digital", "Smart", "Cyber", "Data", "Cloud", "AI", "Quantum"]
COMPANY_SUFFIXES = ["Solutions", "Systems", "Labs", "Works", "Dynamics", "Industries", "Technologies", "Innovations"]

PROJECT_ADJECTIVES = ["Swift", "Nimble", "Robust", "Elegant", "Seamless", "Dynamic", "Innovative", "Scalable"]
PROJECT_NOUNS = ["Bridge", "Engine", "Framework", "Platform", "Portal", "Gateway", "Network", "Studio"]

PET_NAMES = ["Buddy", "Luna", "Max", "Bella", "Charlie", "Lucy", "Cooper", "Daisy", "Rocky", "Molly"]


@mcp.tool()
async def roll_dice(
    ctx: Context,
    sides: int = 6,
    count: int = 1
) -> Dict[str, Any]:
    """
    Roll dice and return detailed results.
    
    Args:
        sides: Number of sides on each die (4-100)
        count: Number of dice to roll (1-20)
        
    Returns:
        Dictionary containing roll results and statistics
    """
    validate_required_param("sides", sides)
    validate_required_param("count", count)
    
    if sides < 4 or sides > 100:
        raise ValueError("Dice must have between 4 and 100 sides")
    if count < 1 or count > 20:
        raise ValueError("Must roll between 1 and 20 dice")
    
    rolls = [random.randint(1, sides) for _ in range(count)]
    
    return {
        "dice_config": {
            "sides": sides,
            "count": count,
            "notation": f"{count}d{sides}"
        },
        "results": {
            "rolls": rolls,
            "total": sum(rolls),
            "average": round(sum(rolls) / len(rolls), 2),
            "minimum": min(rolls),
            "maximum": max(rolls)
        },
        "statistics": {
            "theoretical_average": (sides + 1) / 2,
            "theoretical_total": count * (sides + 1) / 2,
            "roll_efficiency": sum(rolls) / (count * sides)
        }
    }


@mcp.tool()
async def generate_password(
    ctx: Context,
    length: int = 12,
    include_symbols: bool = True,
    include_numbers: bool = True,
    include_uppercase: bool = True,
    include_lowercase: bool = True
) -> Dict[str, Any]:
    """
    Generate secure random password with customizable options.
    
    Args:
        length: Password length (8-128)
        include_symbols: Include special characters
        include_numbers: Include numeric digits
        include_uppercase: Include uppercase letters
        include_lowercase: Include lowercase letters
        
    Returns:
        Dictionary containing password and strength analysis
    """
    validate_required_param("length", length)
    
    if length < 8 or length > 128:
        raise ValueError("Password length must be between 8 and 128 characters")
    
    # Build character set
    chars = ""
    if include_lowercase:
        chars += string.ascii_lowercase
    if include_uppercase:
        chars += string.ascii_uppercase
    if include_numbers:
        chars += string.digits
    if include_symbols:
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    if not chars:
        raise ValueError("At least one character type must be included")
    
    # Generate password
    password = ''.join(random.choice(chars) for _ in range(length))
    
    # Analyze strength
    strength_score = 0
    strength_factors = []
    
    if length >= 12:
        strength_score += 2
        strength_factors.append("Good length")
    elif length >= 8:
        strength_score += 1
        strength_factors.append("Adequate length")
    
    if include_lowercase and any(c.islower() for c in password):
        strength_score += 1
        strength_factors.append("Contains lowercase")
    
    if include_uppercase and any(c.isupper() for c in password):
        strength_score += 1
        strength_factors.append("Contains uppercase")
    
    if include_numbers and any(c.isdigit() for c in password):
        strength_score += 1
        strength_factors.append("Contains numbers")
    
    if include_symbols and any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        strength_score += 2
        strength_factors.append("Contains symbols")
    
    # Determine strength level
    if strength_score >= 6:
        strength_level = "Very Strong"
    elif strength_score >= 4:
        strength_level = "Strong"
    elif strength_score >= 3:
        strength_level = "Moderate"
    else:
        strength_level = "Weak"
    
    return {
        "password": password,
        "length": length,
        "character_sets": {
            "lowercase": include_lowercase,
            "uppercase": include_uppercase,
            "numbers": include_numbers,
            "symbols": include_symbols
        },
        "strength": {
            "level": strength_level,
            "score": f"{strength_score}/7",
            "factors": strength_factors
        },
        "entropy_bits": len(chars) ** length if len(chars) > 0 else 0
    }


@mcp.tool()
async def random_quote(
    ctx: Context,
    category: str = "programming"
) -> Dict[str, Any]:
    """
    Get random inspirational quote from various categories.
    
    Args:
        category: Quote category (programming, motivational, funny)
        
    Returns:
        Dictionary containing quote and metadata
    """
    validate_required_param("category", category)
    
    category = category.lower()
    quote_db = {
        "programming": PROGRAMMING_QUOTES,
        "motivational": MOTIVATIONAL_QUOTES,
        "funny": FUNNY_QUOTES
    }
    
    if category not in quote_db:
        available = ", ".join(quote_db.keys())
        raise ValueError(f"Unknown category '{category}'. Available: {available}")
    
    quotes = quote_db[category]
    selected_quote = random.choice(quotes)
    
    return {
        "quote": selected_quote,
        "category": category,
        "length": len(selected_quote),
        "word_count": len(selected_quote.split()),
        "available_categories": list(quote_db.keys()),
        "total_quotes_in_category": len(quotes)
    }


@mcp.tool()
async def color_palette(
    ctx: Context,
    base_color: str = "",
    count: int = 5,
    format: str = "hex"
) -> Dict[str, Any]:
    """
    Generate random color palette with optional base color.
    
    Args:
        base_color: Base color in hex format (optional)
        count: Number of colors to generate (1-20)
        format: Output format (hex, rgb, hsl)
        
    Returns:
        Dictionary containing color palette and metadata
    """
    validate_required_param("count", count)
    validate_required_param("format", format)
    
    if count < 1 or count > 20:
        raise ValueError("Color count must be between 1 and 20")
    
    format = format.lower()
    if format not in ["hex", "rgb", "hsl"]:
        raise ValueError("Format must be 'hex', 'rgb', or 'hsl'")
    
    colors = []
    
    for i in range(count):
        # Generate random RGB values
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        
        # Convert to requested format
        if format == "hex":
            color = f"#{r:02x}{g:02x}{b:02x}"
        elif format == "rgb":
            color = f"rgb({r}, {g}, {b})"
        elif format == "hsl":
            # Convert RGB to HSL
            h, s, l = _rgb_to_hsl(r, g, b)
            color = f"hsl({h}, {s}%, {l}%)"
        
        colors.append({
            "color": color,
            "rgb": [r, g, b],
            "hex": f"#{r:02x}{g:02x}{b:02x}",
            "brightness": round((r * 0.299 + g * 0.587 + b * 0.114) / 255, 2)
        })
    
    return {
        "palette": colors,
        "count": count,
        "format": format,
        "base_color": base_color if base_color else None,
        "average_brightness": round(sum(c["brightness"] for c in colors) / count, 2)
    }


@mcp.tool()
async def uuid_generator(
    ctx: Context,
    version: int = 4,
    count: int = 1
) -> Dict[str, Any]:
    """
    Generate UUID(s) of specified version.
    
    Args:
        version: UUID version (1 or 4)
        count: Number of UUIDs to generate (1-50)
        
    Returns:
        Dictionary containing UUIDs and metadata
    """
    validate_required_param("version", version)
    validate_required_param("count", count)
    
    if version not in [1, 4]:
        raise ValueError("Only UUID versions 1 and 4 are supported")
    if count < 1 or count > 50:
        raise ValueError("Count must be between 1 and 50")
    
    uuids = []
    
    for _ in range(count):
        if version == 1:
            new_uuid = str(uuid.uuid1())
        else:  # version 4
            new_uuid = str(uuid.uuid4())
        
        uuids.append({
            "uuid": new_uuid,
            "uppercase": new_uuid.upper(),
            "no_hyphens": new_uuid.replace("-", ""),
            "version": version
        })
    
    return {
        "uuids": uuids,
        "count": count,
        "version": version,
        "format_info": {
            "length_with_hyphens": 36,
            "length_without_hyphens": 32,
            "sections": [8, 4, 4, 4, 12]
        }
    }


@mcp.tool()
async def random_name_generator(
    ctx: Context,
    type: str = "person",
    count: int = 1
) -> Dict[str, Any]:
    """
    Generate random names for various purposes.
    
    Args:
        type: Name type (person, company, project, pet)
        count: Number of names to generate (1-20)
        
    Returns:
        Dictionary containing generated names
    """
    validate_required_param("type", type)
    validate_required_param("count", count)
    
    if count < 1 or count > 20:
        raise ValueError("Count must be between 1 and 20")
    
    type = type.lower()
    names = []
    
    for _ in range(count):
        if type == "person":
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            name = f"{first} {last}"
        elif type == "company":
            prefix = random.choice(COMPANY_PREFIXES)
            suffix = random.choice(COMPANY_SUFFIXES)
            name = f"{prefix} {suffix}"
        elif type == "project":
            adj = random.choice(PROJECT_ADJECTIVES)
            noun = random.choice(PROJECT_NOUNS)
            name = f"{adj} {noun}"
        elif type == "pet":
            name = random.choice(PET_NAMES)
        else:
            available = "person, company, project, pet"
            raise ValueError(f"Unknown type '{type}'. Available: {available}")
        
        names.append(name)
    
    return {
        "names": names,
        "type": type,
        "count": count,
        "available_types": ["person", "company", "project", "pet"]
    }


def _rgb_to_hsl(r: int, g: int, b: int) -> tuple:
    """Convert RGB to HSL color space."""
    r, g, b = r/255.0, g/255.0, b/255.0
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    h, s, l = 0, 0, (max_val + min_val) / 2
    
    if max_val == min_val:
        h = s = 0  # achromatic
    else:
        d = max_val - min_val
        s = d / (2 - max_val - min_val) if l > 0.5 else d / (max_val + min_val)
        
        if max_val == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif max_val == g:
            h = (b - r) / d + 2
        elif max_val == b:
            h = (r - g) / d + 4
        h /= 6
    
    return round(h * 360), round(s * 100), round(l * 100)
