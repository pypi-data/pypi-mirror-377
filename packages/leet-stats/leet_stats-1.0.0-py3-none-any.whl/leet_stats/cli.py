#!/usr/bin/env python3
"""
Main CLI module for leet-stats.
"""

import argparse
import sys
from .api import LeetCodeAPI
from .friends import FriendsManager
from .display import StatsDisplay


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="LeetCode Stats CLI - View your LeetCode statistics and compare with friends",
        prog="leet-stats"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Command: leet-stats [username]
    parser_stats = subparsers.add_parser("stats", help="Show LeetCode stats for a user")
    parser_stats.add_argument("username", help="LeetCode username")
    
    # Command: leet-stats add [username]
    parser_add = subparsers.add_parser("add", help="Add a friend to your friends list")
    parser_add.add_argument("username", help="LeetCode username to add as friend")
    
    # Command: leet-stats remove [username]
    parser_remove = subparsers.add_parser("remove", help="Remove a friend from your friends list")
    parser_remove.add_argument("username", help="LeetCode username to remove")
    
    # Command: leet-stats list
    parser_list = subparsers.add_parser("list", help="List all your friends")
    
    # Command: leet-stats rank
    parser_rank = subparsers.add_parser("rank", help="Show ranking of your friends")
    
    # If no command is provided, treat the first argument as username for stats
    if len(sys.argv) == 2 and not sys.argv[1].startswith('-') and sys.argv[1] not in ['stats', 'add', 'remove', 'list', 'rank']:
        # Direct username lookup: leet-stats username
        username = sys.argv[1]
        show_user_stats(username)
        return
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "stats":
            show_user_stats(args.username)
        elif args.command == "add":
            add_friend(args.username)
        elif args.command == "remove":
            remove_friend(args.username)
        elif args.command == "list":
            list_friends()
        elif args.command == "rank":
            show_friends_ranking()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def show_user_stats(username):
    """Show LeetCode stats for a specific user."""
    api = LeetCodeAPI()
    display = StatsDisplay()
    
    try:
        stats = api.get_user_stats(username)
        display.show_user_stats(username, stats)
    except Exception as e:
        print(f"Error fetching stats for {username}: {e}", file=sys.stderr)
        sys.exit(1)


def add_friend(username):
    """Add a friend to the friends list."""
    friends_manager = FriendsManager()
    api = LeetCodeAPI()
    
    try:
        # Verify the user exists by fetching their stats
        api.get_user_stats(username)
        friends_manager.add_friend(username)
        print(f"✅ Added {username} to your friends list!")
    except Exception as e:
        print(f"Error adding friend {username}: {e}", file=sys.stderr)
        sys.exit(1)


def remove_friend(username):
    """Remove a friend from the friends list."""
    friends_manager = FriendsManager()
    
    try:
        friends_manager.remove_friend(username)
        print(f"✅ Removed {username} from your friends list!")
    except Exception as e:
        print(f"Error removing friend {username}: {e}", file=sys.stderr)
        sys.exit(1)


def list_friends():
    """List all friends."""
    friends_manager = FriendsManager()
    friends = friends_manager.get_friends()
    
    if not friends:
        print("No friends added yet. Use 'leet-stats add <username>' to add friends!")
        return
    
    print("📋 Your LeetCode Friends:")
    for i, friend in enumerate(friends, 1):
        print(f"  {i}. {friend}")


def show_friends_ranking():
    """Show ranking of all friends."""
    friends_manager = FriendsManager()
    api = LeetCodeAPI()
    display = StatsDisplay()
    
    friends = friends_manager.get_friends()
    
    if not friends:
        print("No friends added yet. Use 'leet-stats add <username>' to add friends!")
        return
    
    print("🏆 Friends Ranking:")
    print("=" * 50)
    
    friends_stats = []
    
    for friend in friends:
        try:
            stats = api.get_user_stats(friend)
            friends_stats.append((friend, stats))
        except Exception as e:
            print(f"⚠️  Could not fetch stats for {friend}: {e}")
    
    if not friends_stats:
        print("No valid friends data available.")
        return
    
    # Sort by total solved problems (descending)
    friends_stats.sort(key=lambda x: x[1]['totalSolved'], reverse=True)
    
    for i, (username, stats) in enumerate(friends_stats, 1):
        print(f"\n#{i} {username}")
        display.show_compact_stats(stats)
