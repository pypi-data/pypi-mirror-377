#!/usr/bin/env python3
"""
Friends management module for leet-stats.
"""

import json
import os
from pathlib import Path


class FriendsManager:
    """Manages the friends list for the LeetCode stats CLI."""
    
    def __init__(self):
        """Initialize the friends manager."""
        self.config_dir = Path.home() / ".leet-stats"
        self.friends_file = self.config_dir / "friends.json"
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Ensure the config directory exists."""
        self.config_dir.mkdir(exist_ok=True)
    
    def _load_friends(self):
        """Load friends list from file."""
        if not self.friends_file.exists():
            return []
        
        try:
            with open(self.friends_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    
    def _save_friends(self, friends):
        """Save friends list to file."""
        try:
            with open(self.friends_file, 'w') as f:
                json.dump(friends, f, indent=2)
        except IOError as e:
            raise Exception(f"Could not save friends list: {e}")
    
    def add_friend(self, username):
        """Add a friend to the friends list."""
        friends = self._load_friends()
        
        if username in friends:
            raise Exception(f"{username} is already in your friends list!")
        
        friends.append(username)
        self._save_friends(friends)
    
    def remove_friend(self, username):
        """Remove a friend from the friends list."""
        friends = self._load_friends()
        
        if username not in friends:
            raise Exception(f"{username} is not in your friends list!")
        
        friends.remove(username)
        self._save_friends(friends)
    
    def get_friends(self):
        """Get the list of friends."""
        return self._load_friends()
    
    def is_friend(self, username):
        """Check if a username is in the friends list."""
        return username in self._load_friends()
