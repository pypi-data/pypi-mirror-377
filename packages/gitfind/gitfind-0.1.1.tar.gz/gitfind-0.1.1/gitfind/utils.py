"""Utility functions for gitfind."""

from datetime import datetime
from typing import Dict, Any

def format_date(date_string: str) -> str:
    """
    Format a date string to a more readable format.
    
    Args:
        date_string (str): ISO format date string
        
    Returns:
        str: Formatted date string (YYYY-MM-DD)
    """
    if not date_string:
        return "Unknown"
    
    try:
        date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return date_obj.strftime("%Y-%m-%d")
    except (ValueError, AttributeError):
        return "Unknown"

def process_languages(languages_data: Dict[str, int]) -> str:
    """
    Process languages data to get primary languages.
    
    Args:
        languages_data (dict): Dictionary of languages and their byte counts
        
    Returns:
        str: Comma-separated list of primary languages (top 3)
    """
    if not languages_data:
        return "Not specified"
    
    total_bytes = sum(languages_data.values())
    languages = []
    
    for lang, bytes_count in languages_data.items():
        percentage = (bytes_count / total_bytes) * 100
        if percentage >= 1:  # Include languages with at least 1% contribution
            languages.append((lang, percentage))
    
    # Sort by percentage descending
    languages.sort(key=lambda x: x[1], reverse=True)
    
    # Return top 3 languages
    return ", ".join([lang for lang, _ in languages[:3]]) if languages else "Not specified"

def generate_summary(repo_data: Dict[str, Any], languages_data: Dict[str, int], contributors_count: int) -> str:
    """
    Generate a short summary of the repository.
    
    Args:
        repo_data (dict): Repository data from GitHub API
        languages_data (dict): Languages data from GitHub API
        contributors_count (int): Number of contributors
        
    Returns:
        str: Generated summary report
    """
    repo_name = repo_data.get('name', 'Unknown repository')
    stars = repo_data.get('stargazers_count', 0)
    forks = repo_data.get('forks_count', 0)
    description = repo_data.get('description', '')
    
    primary_languages = process_languages(languages_data)
    
    summary = f"{repo_name} is a GitHub repository"
    if description:
        summary += f" described as '{description}'."
    else:
        summary += " with no description provided."
    
    summary += f" It has {stars} stars, {forks} forks, and {contributors_count} contributors."
    
    if primary_languages != "Not specified":
        summary += f" The primary programming languages are {primary_languages}."
    
    return summary  