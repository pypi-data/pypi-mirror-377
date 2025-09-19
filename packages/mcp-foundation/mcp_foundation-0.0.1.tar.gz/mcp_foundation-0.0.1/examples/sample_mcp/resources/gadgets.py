"""
Gadgets resources.

Sample MCP resources for testing functionality with local data sources
and dynamic content generation. All resources are safe and work locally.
"""

import json
import platform
import sys
import os
from datetime import datetime
from typing import Dict, Any
from fastmcp import Context
from mcp_foundation.server.mcp_server import get_mcp

mcp = get_mcp()


@mcp.resource("gadgets://system/info")
async def system_info_resource(ctx: Context) -> str:
    """
    Live system information in JSON format.
    
    Returns comprehensive system details including OS, Python, and environment info.
    """
    system_info = {
        "system": {
            "platform": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "architecture": platform.architecture()[0]
        },
        "python": {
            "version": sys.version,
            "version_info": {
                "major": sys.version_info.major,
                "minor": sys.version_info.minor,
                "micro": sys.version_info.micro
            },
            "executable": sys.executable,
            "platform": sys.platform,
            "implementation": platform.python_implementation()
        },
        "environment": {
            "user": os.environ.get("USER", os.environ.get("USERNAME", "unknown")),
            "home": os.environ.get("HOME", os.environ.get("USERPROFILE", "unknown")),
            "shell": os.environ.get("SHELL", "unknown"),
            "path_entries": len(os.environ.get("PATH", "").split(os.pathsep)),
            "current_directory": os.getcwd()
        },
        "timestamp": datetime.now().isoformat(),
        "uptime": "Not available on this platform"
    }
    
    return json.dumps(system_info, indent=2)


@mcp.resource("gadgets://time/zones")
async def timezone_list_resource(ctx: Context) -> str:
    """
    List of available timezones and time information.
    
    Provides basic timezone data and current time in different zones.
    """
    timezones = {
        "supported_zones": {
            "UTC": {"offset": 0, "name": "Coordinated Universal Time"},
            "EST": {"offset": -5, "name": "Eastern Standard Time"},
            "PST": {"offset": -8, "name": "Pacific Standard Time"},
            "CST": {"offset": -6, "name": "Central Standard Time"},
            "MST": {"offset": -7, "name": "Mountain Standard Time"}
        },
        "current_utc": datetime.utcnow().isoformat(),
        "current_local": datetime.now().isoformat(),
        "note": "Simplified timezone support - does not handle DST automatically"
    }
    
    return json.dumps(timezones, indent=2)


@mcp.resource("gadgets://quotes/database")
async def quotes_database_resource(ctx: Context) -> str:
    """
    Database of inspirational quotes organized by category.
    
    Contains programming, motivational, and funny quotes for the random quote tool.
    """
    quotes_db = {
        "categories": {
            "programming": {
                "count": 10,
                "description": "Quotes about programming, coding, and software development",
                "sample_quotes": [
                    "The best way to debug code is to never write bugs in the first place.",
                    "Code is like humor. When you have to explain it, it's bad.",
                    "Programming is thinking, not typing."
                ]
            },
            "motivational": {
                "count": 10,
                "description": "Inspirational and motivational quotes",
                "sample_quotes": [
                    "The way to get started is to quit talking and begin doing.",
                    "Innovation distinguishes between a leader and a follower.",
                    "The future belongs to those who believe in the beauty of their dreams."
                ]
            },
            "funny": {
                "count": 10,
                "description": "Humorous and entertaining quotes",
                "sample_quotes": [
                    "I have not failed. I've just found 10,000 ways that won't work.",
                    "A computer once beat me at chess, but it was no match for me at kick boxing.",
                    "Why do programmers prefer dark mode? Because light attracts bugs!"
                ]
            }
        },
        "total_quotes": 30,
        "last_updated": datetime.now().isoformat(),
        "usage": "Use the random_quote tool to get quotes from these categories"
    }
    
    return json.dumps(quotes_db, indent=2)


@mcp.resource("gadgets://math/constants")
async def math_constants_resource(ctx: Context) -> str:
    """
    Mathematical constants and formulas reference.
    
    Provides common mathematical constants and formula references.
    """
    import math
    
    math_reference = {
        "constants": {
            "pi": {
                "value": math.pi,
                "description": "Ratio of circumference to diameter of a circle",
                "symbol": "π"
            },
            "e": {
                "value": math.e,
                "description": "Euler's number, base of natural logarithm",
                "symbol": "e"
            },
            "tau": {
                "value": math.tau,
                "description": "Ratio of circumference to radius (2π)",
                "symbol": "τ"
            },
            "golden_ratio": {
                "value": (1 + math.sqrt(5)) / 2,
                "description": "Golden ratio, phi",
                "symbol": "φ"
            }
        },
        "formulas": {
            "quadratic": "ax² + bx + c = 0",
            "quadratic_solution": "x = (-b ± √(b²-4ac)) / 2a",
            "fibonacci": "F(n) = F(n-1) + F(n-2), F(0)=0, F(1)=1",
            "factorial": "n! = n × (n-1) × (n-2) × ... × 1",
            "gcd_relation": "gcd(a,b) × lcm(a,b) = a × b"
        },
        "sequences": {
            "fibonacci": "0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, ...",
            "primes": "2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, ...",
            "squares": "1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, 169, ..."
        },
        "tools_available": [
            "calculate_fibonacci",
            "solve_quadratic", 
            "prime_numbers",
            "factorial",
            "gcd_lcm"
        ]
    }
    
    return json.dumps(math_reference, indent=2)


@mcp.resource("gadgets://demo/data/{data_type}")
async def demo_data_resource(ctx: Context, data_type: str) -> str:
    """
    Generate demo data for testing purposes.
    
    Args:
        data_type: Type of demo data (users, products, orders, companies)
        
    Returns:
        JSON string containing sample data of the requested type
    """
    import random
    
    if data_type == "users":
        demo_data = {
            "users": [
                {
                    "id": i + 1,
                    "name": f"User {i + 1}",
                    "email": f"user{i + 1}@example.com",
                    "age": random.randint(18, 65),
                    "city": random.choice(["New York", "San Francisco", "Chicago", "Austin", "Seattle"]),
                    "active": random.choice([True, False])
                }
                for i in range(10)
            ]
        }
    elif data_type == "products":
        demo_data = {
            "products": [
                {
                    "id": i + 1,
                    "name": f"Product {i + 1}",
                    "price": round(random.uniform(10.0, 500.0), 2),
                    "category": random.choice(["Electronics", "Books", "Clothing", "Home", "Sports"]),
                    "in_stock": random.randint(0, 100),
                    "rating": round(random.uniform(1.0, 5.0), 1)
                }
                for i in range(15)
            ]
        }
    elif data_type == "orders":
        demo_data = {
            "orders": [
                {
                    "id": i + 1,
                    "user_id": random.randint(1, 10),
                    "product_id": random.randint(1, 15),
                    "quantity": random.randint(1, 5),
                    "total": round(random.uniform(20.0, 1000.0), 2),
                    "status": random.choice(["pending", "shipped", "delivered", "cancelled"]),
                    "order_date": f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
                }
                for i in range(20)
            ]
        }
    elif data_type == "companies":
        demo_data = {
            "companies": [
                {
                    "id": i + 1,
                    "name": f"Company {i + 1}",
                    "industry": random.choice(["Technology", "Healthcare", "Finance", "Education", "Retail"]),
                    "employees": random.randint(10, 5000),
                    "revenue": random.randint(100000, 50000000),
                    "founded": random.randint(1990, 2020),
                    "public": random.choice([True, False])
                }
                for i in range(8)
            ]
        }
    else:
        demo_data = {
            "error": f"Unknown data type: {data_type}",
            "available_types": ["users", "products", "orders", "companies"],
            "example_usage": "gadgets://demo/data/users"
        }
    
    demo_data["metadata"] = {
        "generated_at": datetime.now().isoformat(),
        "data_type": data_type,
        "count": len(demo_data.get(data_type, [])) if data_type in demo_data else 0
    }
    
    return json.dumps(demo_data, indent=2)
