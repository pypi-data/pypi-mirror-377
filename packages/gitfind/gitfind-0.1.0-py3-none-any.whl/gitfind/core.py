"""Core functionality for gitfind."""

import requests
from typing import Dict, Any
from datetime import datetime
from .utils import format_date, process_languages, generate_summary

class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors."""
    pass

def repo_summary(url: str) -> Dict[str, Any]:
    """
    Generate a summary of a GitHub repository.
    
    Args:
        url (str): The GitHub repository URL
        
    Returns:
        dict: A dictionary containing repository information
        
    Raises:
        GitHubAPIError: If there's an error accessing the GitHub API
        ValueError: If the URL is invalid or repository is not found
    """
    # Validate and extract owner/repo from URL
    if not url.startswith("https://github.com/"):
        raise ValueError("Invalid GitHub URL. Must start with 'https://github.com/'")
    
    parts = url.rstrip('/').split('/')
    if len(parts) < 5:
        raise ValueError("Invalid GitHub URL format")
    
    owner, repo = parts[-2], parts[-1]
    
    # GitHub API endpoint
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        repo_data = response.json()
        
        # Get contributors
        contributors_url = repo_data.get('contributors_url')
        contributors_response = requests.get(contributors_url, timeout=10)
        contributors = contributors_response.json() if contributors_response.status_code == 200 else []
        
        # Get languages
        languages_url = repo_data.get('languages_url')
        languages_response = requests.get(languages_url, timeout=10)
        languages_data = languages_response.json() if languages_response.status_code == 200 else {}
        
        # Get latest commit date from commits API
        commits_url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        commits_response = requests.get(commits_url, timeout=10)
        commits_data = commits_response.json() if commits_response.status_code == 200 else []
        last_commit_date = commits_data[0]['commit']['author']['date'] if commits_data else repo_data.get('pushed_at')
        
        # Format the response with exact field names as requested
        summary = {
            "Total Stars": repo_data.get('stargazers_count', 0),
            "Total Forks": repo_data.get('forks_count', 0),
            "Total Contributors": len(contributors),
            "Last Commit Date": format_date(last_commit_date),
            "Primary Programming Languages": process_languages(languages_data),
            "Auto-generated summary report": generate_summary(repo_data, languages_data, len(contributors)),
            "Repository URL": url,
            "Description": repo_data.get('description', 'No description available')
        }
        
        return summary
        
    except requests.exceptions.RequestException as e:
        raise GitHubAPIError(f"Error accessing GitHub API: {str(e)}")
    except ValueError as e:
        raise GitHubAPIError(f"Error parsing response: {str(e)}")
    except Exception as e:
        raise GitHubAPIError(f"Unexpected error: {str(e)}")