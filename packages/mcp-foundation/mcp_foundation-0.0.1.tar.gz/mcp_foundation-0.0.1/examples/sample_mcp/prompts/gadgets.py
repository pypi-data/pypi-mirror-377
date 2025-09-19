"""
Gadgets prompts.

Sample MCP prompts for testing functionality with various AI-assisted
tasks including code review, debugging, explanations, and creative writing.
"""

from typing import Dict, Any, List
from fastmcp import Context
from mcp_foundation.server.mcp_server import 

mcp = get_mcp()


@mcp.prompt()
async def code_review_prompt(
    ctx: Context,
    code: str,
    language: str = "python",
    focus: str = "general"
) -> Dict[str, Any]:
    """
    Generate a comprehensive code review prompt with specific focus areas.
    
    Args:
        code: Code to review
        language: Programming language (python, javascript, java, etc.)
        focus: Review focus (general, security, performance, style, bugs)
        
    Returns:
        Structured prompt for code review
    """
    focus_areas = {
        "general": "overall code quality, readability, and best practices",
        "security": "security vulnerabilities, input validation, and secure coding practices",
        "performance": "performance optimization, efficiency, and scalability",
        "style": "code style, formatting, naming conventions, and documentation",
        "bugs": "potential bugs, logic errors, and edge cases"
    }
    
    focus_description = focus_areas.get(focus.lower(), focus_areas["general"])
    
    prompt_text = f"""Please review the following {language} code with a focus on {focus_description}.

**Code to Review:**
```{language}
{code}
```

**Review Guidelines:**
1. **Code Quality**: Assess overall structure, organization, and clarity
2. **Best Practices**: Check adherence to {language} best practices and conventions
3. **Potential Issues**: Identify bugs, edge cases, or problematic patterns
4. **Improvements**: Suggest specific improvements and optimizations
5. **Documentation**: Evaluate comments, docstrings, and self-documenting code

**Focus Area: {focus.title()}**
{focus_description}

**Please provide:**
- **Summary**: Brief overall assessment
- **Strengths**: What the code does well
- **Issues**: Specific problems or concerns (with line references if applicable)
- **Recommendations**: Actionable suggestions for improvement
- **Rating**: Code quality score (1-10) with justification

**Format your response with clear sections and be constructive in your feedback.**"""

    return {
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": prompt_text
                }
            }
        ],
        "metadata": {
            "code_length": len(code),
            "language": language,
            "focus": focus,
            "prompt_type": "code_review"
        }
    }


@mcp.prompt()
async def debug_helper_prompt(
    ctx: Context,
    error_message: str,
    code_context: str = "",
    language: str = "python"
) -> Dict[str, Any]:
    """
    Generate a debugging assistance prompt for troubleshooting errors.
    
    Args:
        error_message: The error message or description
        code_context: Relevant code context (optional)
        language: Programming language
        
    Returns:
        Structured prompt for debugging assistance
    """
    prompt_text = f"""Help me debug this {language} error:

**Error Message:**
```
{error_message}
```

**Code Context:**
```{language}
{code_context if code_context else "No code context provided"}
```

**Debugging Request:**
Please help me understand and resolve this error by providing:

1. **Error Analysis**:
   - What this error means in plain English
   - Common causes of this type of error
   - Why this error might be occurring in this context

2. **Troubleshooting Steps**:
   - Step-by-step debugging approach
   - Specific things to check or verify
   - Questions to ask about the code/environment

3. **Potential Solutions**:
   - Multiple possible fixes ranked by likelihood
   - Code examples showing corrections
   - Best practices to prevent similar errors

4. **Prevention**:
   - How to avoid this error in the future
   - Defensive coding practices
   - Testing strategies

**Please be thorough but practical in your response.**"""

    return {
        "messages": [
            {
                "role": "user", 
                "content": {
                    "type": "text",
                    "text": prompt_text
                }
            }
        ],
        "metadata": {
            "error_message": error_message,
            "has_code_context": bool(code_context.strip()),
            "language": language,
            "prompt_type": "debug_helper"
        }
    }


@mcp.prompt()
async def explain_concept_prompt(
    ctx: Context,
    concept: str,
    audience: str = "beginner",
    format: str = "tutorial"
) -> Dict[str, Any]:
    """
    Generate an educational explanation prompt for technical concepts.
    
    Args:
        concept: Technical concept to explain
        audience: Target audience (beginner, intermediate, advanced)
        format: Explanation format (tutorial, reference, example, analogy)
        
    Returns:
        Structured prompt for concept explanation
    """
    audience_levels = {
        "beginner": "someone new to the topic with minimal background knowledge",
        "intermediate": "someone with some experience who wants to deepen understanding",
        "advanced": "an experienced practitioner looking for comprehensive details"
    }
    
    format_styles = {
        "tutorial": "step-by-step tutorial with practical examples",
        "reference": "comprehensive reference guide with detailed explanations",
        "example": "example-driven explanation with real-world use cases",
        "analogy": "analogy-based explanation using familiar comparisons"
    }
    
    audience_desc = audience_levels.get(audience.lower(), audience_levels["beginner"])
    format_desc = format_styles.get(format.lower(), format_styles["tutorial"])
    
    prompt_text = f"""Please explain "{concept}" for {audience_desc} in a {format_desc} format.

**Explanation Requirements:**

1. **Introduction**: Start with a clear, simple definition
2. **Context**: Explain why this concept is important and when it's used
3. **Core Principles**: Break down the fundamental ideas
4. **Practical Examples**: Provide concrete, relatable examples
5. **Common Pitfalls**: Highlight typical misunderstandings or mistakes
6. **Next Steps**: Suggest what to learn next or how to practice

**Audience Level: {audience.title()}**
- Assume the reader is {audience_desc}
- Adjust technical depth and terminology appropriately
- Include prerequisite knowledge if needed

**Format Style: {format.title()}**
- Structure the explanation as a {format_desc}
- Use appropriate headings, examples, and explanations
- Make it engaging and easy to follow

**Additional Guidelines:**
- Use clear, accessible language
- Include diagrams or code examples where helpful
- Provide real-world applications and use cases
- End with resources for further learning

Please make this explanation comprehensive yet approachable for the intended audience."""

    return {
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text", 
                    "text": prompt_text
                }
            }
        ],
        "metadata": {
            "concept": concept,
            "audience": audience,
            "format": format,
            "prompt_type": "explain_concept"
        }
    }


@mcp.prompt()
async def creative_writing_prompt(
    ctx: Context,
    genre: str = "sci-fi",
    theme: str = "",
    length: str = "short"
) -> Dict[str, Any]:
    """
    Generate creative writing prompts for various genres and themes.
    
    Args:
        genre: Writing genre (sci-fi, fantasy, mystery, romance, horror, drama)
        theme: Optional theme or topic
        length: Story length (short, medium, long)
        
    Returns:
        Structured prompt for creative writing
    """
    genre_elements = {
        "sci-fi": {
            "setting": "futuristic or alternate reality",
            "elements": "advanced technology, space travel, artificial intelligence",
            "themes": "progress vs. humanity, exploration, ethics of technology"
        },
        "fantasy": {
            "setting": "magical or mythical world",
            "elements": "magic systems, mythical creatures, epic quests",
            "themes": "good vs. evil, coming of age, power and responsibility"
        },
        "mystery": {
            "setting": "contemporary or historical",
            "elements": "puzzles, clues, investigation, suspense",
            "themes": "truth vs. deception, justice, human nature"
        },
        "romance": {
            "setting": "any time period",
            "elements": "relationships, emotional connection, conflict resolution",
            "themes": "love conquers all, personal growth, sacrifice"
        },
        "horror": {
            "setting": "ominous or isolated locations",
            "elements": "supernatural threats, psychological tension, survival",
            "themes": "fear of unknown, human vulnerability, moral choices"
        },
        "drama": {
            "setting": "realistic contemporary or historical",
            "elements": "character development, emotional conflict, real-world issues",
            "themes": "family dynamics, social issues, personal transformation"
        }
    }
    
    length_specs = {
        "short": "1,000-2,500 words (short story)",
        "medium": "5,000-10,000 words (novelette)",
        "long": "15,000+ words (novella or novel beginning)"
    }
    
    genre_info = genre_elements.get(genre.lower(), genre_elements["sci-fi"])
    length_spec = length_specs.get(length.lower(), length_specs["short"])
    
    theme_text = f" with a focus on the theme of '{theme}'" if theme else ""
    
    prompt_text = f"""Create a compelling {genre} story{theme_text} of approximately {length_spec}.

**Genre: {genre.title()}**
- **Setting**: {genre_info['setting']}
- **Key Elements**: {genre_info['elements']}
- **Common Themes**: {genre_info['themes']}

**Story Requirements:**

1. **Opening Hook**: Start with an engaging scene that immediately draws readers in
2. **Character Development**: Create memorable, multi-dimensional characters
3. **Plot Structure**: Develop a clear beginning, rising action, climax, and resolution
4. **Setting & Atmosphere**: Establish a vivid, immersive world
5. **Dialogue**: Write natural, character-appropriate dialogue
6. **Theme Integration**: Weave thematic elements throughout the narrative

**Specific Guidelines:**
- **Target Length**: {length_spec}
- **Genre Conventions**: Honor {genre} traditions while adding original elements
{f'- **Theme Focus**: Explore and develop the theme of "{theme}"' if theme else ''}
- **Audience**: Write for adult readers who enjoy {genre} fiction

**Writing Style:**
- Use descriptive but accessible prose
- Balance action, dialogue, and exposition
- Create emotional resonance with readers
- End with a satisfying conclusion

**Additional Inspiration:**
Consider incorporating current events, personal experiences, or philosophical questions that resonate with modern readers while staying true to the {genre} genre.

Please write a complete story that demonstrates strong storytelling fundamentals and genre mastery."""

    return {
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": prompt_text
                }
            }
        ],
        "metadata": {
            "genre": genre,
            "theme": theme if theme else "none specified",
            "length": length,
            "prompt_type": "creative_writing"
        }
    }


@mcp.prompt()
async def brainstorm_prompt(
    ctx: Context,
    topic: str,
    goal: str = "ideas",
    constraints: str = ""
) -> Dict[str, Any]:
    """
    Generate brainstorming session prompts for idea generation.
    
    Args:
        topic: Topic or problem to brainstorm about
        goal: Brainstorming goal (ideas, solutions, innovations, improvements)
        constraints: Any constraints or limitations to consider
        
    Returns:
        Structured prompt for brainstorming session
    """
    goal_descriptions = {
        "ideas": "generate creative and diverse ideas",
        "solutions": "find practical solutions to problems",
        "innovations": "discover innovative approaches and breakthroughs",
        "improvements": "identify ways to enhance or optimize existing things"
    }
    
    goal_desc = goal_descriptions.get(goal.lower(), goal_descriptions["ideas"])
    constraints_text = f"\n\n**Constraints to Consider:**\n{constraints}" if constraints else ""
    
    prompt_text = f"""Let's brainstorm about "{topic}" with the goal to {goal_desc}.

**Brainstorming Session Guidelines:**

1. **Divergent Thinking**: Generate as many ideas as possible without immediate judgment
2. **Build on Ideas**: Expand and combine concepts to create new possibilities
3. **Think Outside the Box**: Challenge assumptions and explore unconventional approaches
4. **Quantity First**: Prioritize volume of ideas over initial quality
5. **Wild Ideas Welcome**: Embrace seemingly impossible or impractical concepts

**Session Structure:**

**Phase 1: Idea Generation**
- List 15-20 initial ideas related to {topic}
- Range from practical to wildly creative
- Don't filter or critique yet

**Phase 2: Idea Development**
- Select the 5 most promising ideas
- Develop each with more detail
- Consider implementation approaches

**Phase 3: Combination & Innovation**
- Combine different ideas to create hybrid solutions
- Look for unexpected connections
- Push boundaries further

**Phase 4: Practical Assessment**
- Evaluate feasibility and impact
- Identify quick wins vs. long-term projects
- Consider resource requirements

**Topic Focus: {topic}**
**Goal: {goal_desc.title()}**{constraints_text}

**Brainstorming Techniques to Use:**
- Mind mapping and association
- "What if..." scenarios
- Reverse brainstorming (what would make this worse?)
- Random word association
- Role-playing different perspectives

Please facilitate an energetic, creative brainstorming session that produces actionable insights and innovative thinking about this topic."""

    return {
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": prompt_text
                }
            }
        ],
        "metadata": {
            "topic": topic,
            "goal": goal,
            "has_constraints": bool(constraints.strip()),
            "prompt_type": "brainstorm"
        }
    }
