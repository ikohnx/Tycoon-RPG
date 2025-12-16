#!/usr/bin/env python3
"""
Business Tycoon RPG - Main Game Entry Point

A 2D educational RPG teaching real-world business skills across 
6 Core Disciplines and 8 Sub-Skills with a 10-Level progression system.

MVP: Modern World / Restaurant Industry / Marketing Discipline
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import init_database, seed_scenarios
from src.game_engine import (
    GameEngine, 
    display_scenario, 
    display_result, 
    display_player_stats
)


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """Print the game header."""
    print("\n" + "=" * 60)
    print("          🏢 BUSINESS TYCOON RPG 🏢")
    print("     Master Business Skills Across Three Worlds")
    print("=" * 60)


def main_menu():
    """Display the main menu and get player choice."""
    print("\n📋 MAIN MENU")
    print("-" * 40)
    print("  1) New Game")
    print("  2) Continue Game")
    print("  3) View Leaderboard")
    print("  4) Exit")
    print("-" * 40)
    
    while True:
        choice = input("Enter choice (1-4): ").strip()
        if choice in ['1', '2', '3', '4']:
            return choice
        print("Invalid choice. Please enter 1-4.")


def select_world():
    """Let player select their starting world."""
    print("\n🌍 SELECT YOUR WORLD")
    print("-" * 40)
    print("  1) Modern World - Contemporary business environment")
    print("     (Office towers, digital marketing, stock markets)")
    print()
    print("  2) Fantasy World - Medieval magical realm [Coming Soon]")
    print("     (Taverns, dragon-scale trade, gold-backed loans)")
    print()
    print("  3) Sci-Fi World - Futuristic galactic economy [Coming Soon]")
    print("     (Starship commerce, rare-earth mining, AI assistants)")
    print("-" * 40)
    
    while True:
        choice = input("Enter choice (1-3): ").strip()
        if choice == '1':
            return "Modern"
        elif choice in ['2', '3']:
            print("This world is coming soon! Please select Modern for now.")
        else:
            print("Invalid choice. Please enter 1-3.")


def select_industry():
    """Let player select their starting industry."""
    print("\n🏭 SELECT YOUR INDUSTRY")
    print("-" * 40)
    print("  1) Restaurant - Food service and hospitality")
    print("     (Marketing bonus: +20% EXP, Legal penalty: -20% EXP)")
    print()
    print("  2) SaaS (Software) - Tech startup [Coming Soon]")
    print("  3) Retail - Physical goods sales [Coming Soon]")
    print("  4) Construction - Building and development [Coming Soon]")
    print("-" * 40)
    
    while True:
        choice = input("Enter choice (1-4): ").strip()
        if choice == '1':
            return "Restaurant"
        elif choice in ['2', '3', '4']:
            print("This industry is coming soon! Please select Restaurant for now.")
        else:
            print("Invalid choice. Please enter 1-4.")


def game_hub(engine):
    """Main game hub - central navigation point."""
    while True:
        stats = engine.get_player_stats()
        
        print("\n" + "=" * 60)
        print(f"🏠 {stats['name']}'s Business HQ | Month {stats['month']}")
        print(f"💰 ${stats['cash']:,.2f} | ⭐ Reputation: {stats['reputation']}/100")
        print("=" * 60)
        print("\n📋 WHAT WOULD YOU LIKE TO DO?")
        print("-" * 40)
        print("  1) Take on Marketing Challenges")
        print("  2) View My Progress")
        print("  3) Save and Return to Main Menu")
        print("-" * 40)
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == '1':
            play_scenarios(engine, "Marketing")
        elif choice == '2':
            display_player_stats(stats)
            input("\nPress Enter to continue...")
        elif choice == '3':
            engine.current_player.save_to_db()
            print("\n💾 Game saved!")
            break
        else:
            print("Invalid choice.")


def play_scenarios(engine, discipline):
    """Play through available scenarios for a discipline."""
    while True:
        scenarios = engine.get_available_scenarios(discipline)
        
        if not scenarios:
            print(f"\n🎉 No more {discipline} scenarios available at your current level!")
            print("Level up to unlock more challenges!")
            input("\nPress Enter to continue...")
            return
        
        print(f"\n📚 Available {discipline} Scenarios: {len(scenarios)}")
        print("-" * 40)
        
        for i, scenario in enumerate(scenarios[:5], 1):
            level_req = scenario['required_level']
            print(f"  {i}) [L{level_req}] {scenario['scenario_title']}")
        
        print(f"\n  0) Return to Hub")
        print("-" * 40)
        
        choice = input("Select a scenario (0 to return): ").strip()
        
        if choice == '0':
            return
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(scenarios[:5]):
                play_single_scenario(engine, scenarios[idx])
            else:
                print("Invalid choice.")
        except ValueError:
            print("Please enter a number.")


def play_single_scenario(engine, scenario):
    """Play through a single scenario."""
    clear_screen()
    display_scenario(scenario)
    
    valid_choices = ['A', 'B']
    if scenario.get('choice_c_text'):
        valid_choices.append('C')
    
    while True:
        choice = input(f"\nYour choice ({'/'.join(valid_choices)}): ").strip().upper()
        if choice in valid_choices:
            break
        print(f"Please enter {', '.join(valid_choices)}")
    
    result = engine.process_choice(scenario, choice)
    
    if result.get('error'):
        print(f"\nError: {result['error']}")
        return
    
    display_result(result)
    input("\nPress Enter to continue...")


def new_game(engine):
    """Start a new game."""
    clear_screen()
    print_header()
    
    print("\n👤 CREATE YOUR CHARACTER")
    print("-" * 40)
    name = input("Enter your business name: ").strip()
    
    if not name:
        name = "Entrepreneur"
    
    world = select_world()
    industry = select_industry()
    
    player = engine.create_new_player(name, world, industry)
    
    print(f"\n✨ Welcome, {name}!")
    print(f"   You've started your journey in the {world} World")
    print(f"   building your {industry} business empire!")
    print("\n   Your starting capital: $10,000")
    print("   Your reputation: 50/100")
    print("\n   Complete scenarios to gain EXP and level up your skills!")
    
    input("\nPress Enter to begin your journey...")
    
    game_hub(engine)


def continue_game(engine):
    """Continue an existing game."""
    players = engine.get_all_players()
    
    if not players:
        print("\n❌ No saved games found. Start a new game!")
        return
    
    print("\n💾 SAVED GAMES")
    print("-" * 40)
    
    for i, player in enumerate(players, 1):
        print(f"  {i}) {player['player_name']} - {player['chosen_world']}/{player['chosen_industry']}")
        print(f"     Cash: ${float(player['total_cash']):,.2f}")
    
    print(f"\n  0) Back to Main Menu")
    print("-" * 40)
    
    while True:
        choice = input("Select a save (0 to cancel): ").strip()
        
        if choice == '0':
            return
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(players):
                player = engine.load_player(players[idx]['player_id'])
                print(f"\n✨ Welcome back, {player.name}!")
                game_hub(engine)
                return
            else:
                print("Invalid choice.")
        except ValueError:
            print("Please enter a number.")


def view_leaderboard(engine):
    """View the leaderboard of players."""
    players = engine.get_all_players()
    
    print("\n🏆 LEADERBOARD")
    print("-" * 40)
    
    if not players:
        print("No players yet. Be the first!")
    else:
        for i, player in enumerate(players[:10], 1):
            print(f"  {i}. {player['player_name']} - ${float(player['total_cash']):,.2f}")
    
    input("\nPress Enter to continue...")


def main():
    """Main game entry point."""
    print("Initializing Business Tycoon RPG...")
    
    try:
        init_database()
        seed_scenarios()
    except Exception as e:
        print(f"Database initialization error: {e}")
        print("Make sure DATABASE_URL is set correctly.")
        return
    
    engine = GameEngine()
    
    while True:
        clear_screen()
        print_header()
        
        choice = main_menu()
        
        if choice == '1':
            new_game(engine)
        elif choice == '2':
            continue_game(engine)
        elif choice == '3':
            view_leaderboard(engine)
        elif choice == '4':
            print("\n👋 Thanks for playing Business Tycoon RPG!")
            print("   See you next time, future tycoon!")
            break


if __name__ == "__main__":
    main()
