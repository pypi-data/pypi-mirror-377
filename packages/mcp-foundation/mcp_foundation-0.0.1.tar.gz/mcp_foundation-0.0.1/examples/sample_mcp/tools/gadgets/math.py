"""Math calculation gadgets."""

import math
from typing import Dict, Any, List
from fastmcp import Context
from mcp_foundation.server.context import get_mcp
from ..utils.validate import validate_required_param

mcp = get_mcp()


@mcp.tool()
async def calculate_fibonacci(ctx: Context, n: int) -> Dict[str, Any]:
    """Calculate Fibonacci sequence up to n numbers (max 50)."""
    validate_required_param("n", n)
    
    if n <= 0:
        raise ValueError("n must be a positive integer")
    if n > 50:
        raise ValueError("n cannot exceed 50 (too computationally expensive)")
    
    sequence = []
    a, b = 0, 1
    
    for i in range(n):
        sequence.append(a)
        a, b = b, a + b
    
    return {
        "sequence": sequence,
        "count": len(sequence),
        "last_number": sequence[-1] if sequence else 0,
        "sum": sum(sequence)
    }


@mcp.tool()
async def solve_quadratic(ctx: Context, a: float, b: float, c: float) -> Dict[str, Any]:
    """Solve quadratic equation ax² + bx + c = 0."""
    validate_required_param("a", a)
    validate_required_param("b", b)
    validate_required_param("c", c)
    
    if a == 0:
        raise ValueError("Coefficient 'a' cannot be zero for quadratic equation")
    
    discriminant = b**2 - 4*a*c
    
    result = {
        "equation": f"{a}x² + {b}x + {c} = 0",
        "discriminant": discriminant
    }
    
    if discriminant > 0:
        x1 = (-b + math.sqrt(discriminant)) / (2*a)
        x2 = (-b - math.sqrt(discriminant)) / (2*a)
        result.update({
            "solution_type": "two_real_roots",
            "solutions": [x1, x2]
        })
    elif discriminant == 0:
        x = -b / (2*a)
        result.update({
            "solution_type": "one_real_root",
            "solutions": [x]
        })
    else:
        real_part = -b / (2*a)
        imaginary_part = math.sqrt(-discriminant) / (2*a)
        result.update({
            "solution_type": "complex_roots",
            "solutions": [
                f"{real_part} + {imaginary_part}i",
                f"{real_part} - {imaginary_part}i"
            ]
        })
    
    return result


@mcp.tool()
async def prime_numbers(ctx: Context, limit: int) -> Dict[str, Any]:
    """Find all prime numbers up to the given limit using Sieve of Eratosthenes (max 1000)."""
    validate_required_param("limit", limit)
    
    if limit < 2:
        return {
            "primes": [],
            "count": 0,
            "limit": limit,
            "largest_prime": None
        }
    
    if limit > 1000:
        raise ValueError("Limit cannot exceed 1000 (too computationally expensive)")
    
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    
    for i in range(2, int(math.sqrt(limit)) + 1):
        if sieve[i]:
            for j in range(i*i, limit + 1, i):
                sieve[j] = False
    
    primes = [i for i in range(2, limit + 1) if sieve[i]]
    
    return {
        "primes": primes,
        "count": len(primes),
        "limit": limit,
        "largest_prime": primes[-1] if primes else None,
        "density": len(primes) / limit if limit > 0 else 0
    }


@mcp.tool()
async def factorial(ctx: Context, n: int) -> Dict[str, Any]:
    """Calculate factorial of n (n!) for non-negative integer (max 20)."""
    validate_required_param("n", n)
    
    if n < 0:
        raise ValueError("n must be non-negative")
    if n > 20:
        raise ValueError("n cannot exceed 20 (result too large)")
    
    result = math.factorial(n)
    
    return {
        "input": n,
        "result": result,
        "digits": len(str(result)),
        "formula": f"{n}! = {' × '.join(str(i) for i in range(1, n+1))}" if n > 0 else "0! = 1"
    }


@mcp.tool()
async def gcd_lcm(ctx: Context, a: int, b: int) -> Dict[str, Any]:
    """Calculate Greatest Common Divisor (GCD) and Least Common Multiple (LCM) of two numbers."""
    validate_required_param("a", a)
    validate_required_param("b", b)
    
    a, b = abs(a), abs(b)
    
    if a == 0 and b == 0:
        raise ValueError("Both numbers cannot be zero")
    
    gcd_result = math.gcd(a, b)
    lcm_result = abs(a * b) // gcd_result if gcd_result != 0 else 0
    
    return {
        "numbers": [a, b],
        "gcd": gcd_result,
        "lcm": lcm_result,
        "are_coprime": gcd_result == 1,
        "relationship": f"gcd({a}, {b}) = {gcd_result}, lcm({a}, {b}) = {lcm_result}"
    }
