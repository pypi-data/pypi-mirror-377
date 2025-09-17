"""Tests for gitfind core functionality."""

import pytest
from unittest.mock import patch, Mock
from gitfind.core import repo_summary, GitHubAPIError

@patch('gitfind.core.requests.get')
def test_repo_summary_success(mock_get):
    """Test successful repository summary with exact field names."""
    # Mock the main repository response
    mock_repo_response = Mock()
    mock_repo_response.status_code = 200
    mock_repo_response.json.return_value = {
        'stargazers_count': 150,
        'forks_count': 75,
        'contributors_url': 'https://api.github.com/repos/owner/repo/contributors',
        'languages_url': 'https://api.github.com/repos/owner/repo/languages',
        'pushed_at': '2023-01-01T00:00:00Z',
        'description': 'A test repository for unit testing',
        'name': 'test-repo'
    }
    
    # Mock the contributors response
    mock_contributors_response = Mock()
    mock_contributors_response.status_code = 200
    mock_contributors_response.json.return_value = [{}, {}, {}, {}]  # 4 contributors
    
    # Mock the languages response
    mock_languages_response = Mock()
    mock_languages_response.status_code = 200
    mock_languages_response.json.return_value = {
        'Python': 8000,
        'JavaScript': 2000,
        'HTML': 500
    }
    
    # Mock the commits response
    mock_commits_response = Mock()
    mock_commits_response.status_code = 200
    mock_commits_response.json.return_value = [{
        'commit': {
            'author': {
                'date': '2023-01-01T00:00:00Z'
            }
        }
    }]
    
    # Set up the mock to return different responses for different URLs
    mock_get.side_effect = [
        mock_repo_response,
        mock_contributors_response,
        mock_languages_response,
        mock_commits_response
    ]
    
    result = repo_summary('https://github.com/owner/repo')
    
    # Test exact field names as requested
    assert result['Total Stars'] == 150
    assert result['Total Forks'] == 75
    assert result['Total Contributors'] == 4
    assert result['Last Commit Date'] == '2023-01-01'
    assert result['Primary Programming Languages'] == 'Python, JavaScript, HTML'
    assert 'test-repo' in result['Auto-generated summary report']
    assert '150 stars' in result['Auto-generated summary report']
    assert '75 forks' in result['Auto-generated summary report']

@patch('gitfind.core.requests.get')
def test_repo_summary_invalid_url(mock_get):
    """Test repository summary with invalid URL."""
    with pytest.raises(ValueError, match="Invalid GitHub URL"):
        repo_summary('https://gitlab.com/owner/repo')

@patch('gitfind.core.requests.get')
def test_repo_summary_api_error(mock_get):
    """Test repository summary with API error."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = Exception("Repository not found")
    mock_get.return_value = mock_response
    
    with pytest.raises(GitHubAPIError):
        repo_summary('https://github.com/owner/repo')