#!/usr/bin/env python3
"""
LeetCode API client for leet-stats.
"""

import requests
import json
from typing import Dict, Any


class LeetCodeAPI:
    """Client for the LeetCode API."""
    
    BASE_URL = "https://leetcode-api-faisalshohag.vercel.app"
    
    def __init__(self):
        """Initialize the API client."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'leet-stats-cli/1.0.0'
        })
    
    def get_user_stats(self, username: str) -> Dict[str, Any]:
        """
        Get LeetCode statistics for a user.
        
        Args:
            username: LeetCode username
            
        Returns:
            Dictionary containing user statistics
            
        Raises:
            Exception: If the API request fails or user not found
        """
        url = f"{self.BASE_URL}/{username}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if user exists (API returns empty object for non-existent users)
            if not data or 'totalSolved' not in data:
                raise Exception(f"User '{username}' not found or has no public profile")
            
            return data
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch data from LeetCode API: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid response from LeetCode API: {e}")
    
    def get_user_ranking(self, username: str) -> int:
        """
        Get the ranking of a user.
        
        Args:
            username: LeetCode username
            
        Returns:
            User's ranking
        """
        stats = self.get_user_stats(username)
        return stats.get('ranking', 0)
    
    def get_recent_submissions(self, username: str, limit: int = 10) -> list:
        """
        Get recent submissions for a user.
        
        Args:
            username: LeetCode username
            limit: Maximum number of recent submissions to return
            
        Returns:
            List of recent submissions
        """
        stats = self.get_user_stats(username)
        recent = stats.get('recentSubmissions', [])
        return recent[:limit]
