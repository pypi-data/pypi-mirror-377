#!/usr/bin/env python3
"""
Display module for leet-stats - handles formatting and displaying LeetCode statistics.
"""

from typing import Dict, Any
from datetime import datetime


class StatsDisplay:
    """Handles formatting and displaying LeetCode statistics."""
    
    def __init__(self):
        """Initialize the display formatter."""
        pass
    
    def show_user_stats(self, username: str, stats: Dict[str, Any]):
        """
        Display comprehensive user statistics.
        
        Args:
            username: LeetCode username
            stats: User statistics dictionary
        """
        print(f"\n🔍 LeetCode Stats for @{username}")
        print("=" * 50)
        
        # Overall stats
        total_solved = stats.get('totalSolved', 0)
        total_questions = stats.get('totalQuestions', 0)
        ranking = stats.get('ranking', 0)
        
        print(f"📊 Total Solved: {total_solved}/{total_questions}")
        print(f"🏆 Global Ranking: #{ranking:,}" if ranking > 0 else "🏆 Global Ranking: Not available")
        
        # Difficulty breakdown
        print(f"\n📈 Problems by Difficulty:")
        easy_solved = stats.get('easySolved', 0)
        total_easy = stats.get('totalEasy', 0)
        medium_solved = stats.get('mediumSolved', 0)
        total_medium = stats.get('totalMedium', 0)
        hard_solved = stats.get('hardSolved', 0)
        total_hard = stats.get('totalHard', 0)
        
        print(f"  🟢 Easy:   {easy_solved:3d}/{total_easy:3d} ({self._calculate_percentage(easy_solved, total_easy):5.1f}%)")
        print(f"  🟡 Medium: {medium_solved:3d}/{total_medium:3d} ({self._calculate_percentage(medium_solved, total_medium):5.1f}%)")
        print(f"  🔴 Hard:   {hard_solved:3d}/{total_hard:3d} ({self._calculate_percentage(hard_solved, total_hard):5.1f}%)")
        
        # Submission stats
        print(f"\n📝 Submission Statistics:")
        total_submissions = stats.get('totalSubmissions', [])
        for submission in total_submissions:
            if submission['difficulty'] == 'All':
                print(f"  Total Submissions: {submission['submissions']}")
                break
        
        # Recent submissions
        recent_submissions = stats.get('recentSubmissions', [])[:5]
        if recent_submissions:
            print(f"\n🕒 Recent Submissions:")
            for submission in recent_submissions:
                title = submission.get('title', 'Unknown')
                status = submission.get('statusDisplay', 'Unknown')
                lang = submission.get('lang', 'Unknown')
                timestamp = submission.get('timestamp', '0')
                
                # Convert timestamp to readable date
                try:
                    date = datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d')
                except (ValueError, TypeError):
                    date = 'Unknown date'
                
                status_emoji = self._get_status_emoji(status)
                print(f"  {status_emoji} {title} ({lang}) - {date}")
        
        # Contribution points
        contribution = stats.get('contributionPoint', 0)
        reputation = stats.get('reputation', 0)
        if contribution > 0 or reputation > 0:
            print(f"\n⭐ Contribution Points: {contribution}")
            print(f"⭐ Reputation: {reputation}")
    
    def show_compact_stats(self, stats: Dict[str, Any]):
        """
        Display compact statistics for ranking view.
        
        Args:
            stats: User statistics dictionary
        """
        total_solved = stats.get('totalSolved', 0)
        easy_solved = stats.get('easySolved', 0)
        medium_solved = stats.get('mediumSolved', 0)
        hard_solved = stats.get('hardSolved', 0)
        ranking = stats.get('ranking', 0)
        
        print(f"  📊 Solved: {total_solved} (🟢{easy_solved} 🟡{medium_solved} 🔴{hard_solved})")
        if ranking > 0:
            print(f"  🏆 Rank: #{ranking:,}")
    
    def _calculate_percentage(self, solved: int, total: int) -> float:
        """Calculate percentage with safe division."""
        if total == 0:
            return 0.0
        return (solved / total) * 100
    
    def _get_status_emoji(self, status: str) -> str:
        """Get emoji for submission status."""
        status_emojis = {
            'Accepted': '✅',
            'Wrong Answer': '❌',
            'Runtime Error': '💥',
            'Time Limit Exceeded': '⏰',
            'Memory Limit Exceeded': '💾',
            'Compile Error': '🔧',
            'Output Limit Exceeded': '📤'
        }
        return status_emojis.get(status, '❓')
