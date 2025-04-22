import argparse
import logging
import sys
from datetime import datetime, timedelta
from tabulate import tabulate
from .api_client import OddsApiClient
from .models import GameOdds
from .calculator import EVCalculator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mlb_odds.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("MLBOdds")

def display_games(games):
    """Display games and their odds in a table"""
    rows = []
    
    for game in games:
        home_odds = game.get_best_odds(game.home_team)
        away_odds = game.get_best_odds(game.away_team)
        
        row = [
            game.commence_time.strftime("%Y-%m-%d %H:%M"),
            game.away_team,
            game.home_team,
            f"{away_odds['odds']} ({away_odds['bookmaker']})",
            f"{home_odds['odds']} ({home_odds['bookmaker']})"
        ]
        
        rows.append(row)
    
    print("\nMLB Games and Best Odds:")
    print(tabulate(
        rows,
        headers=["Game Time", "Away Team", "Home Team", "Away Odds", "Home Odds"],
        tablefmt="grid"
    ))

def display_arbitrage(opportunities):
    """Display arbitrage opportunities in a table"""
    if not opportunities:
        print("\nNo arbitrage opportunities found")
        return
    
    rows = []
    
    for opp in opportunities:
        row = [
            opp['game'],
            f"{opp['away_team']['name']} ({opp['away_team']['best_odds']} @ {opp['away_team']['bookmaker']})",
            f"{opp['home_team']['name']} ({opp['home_team']['best_odds']} @ {opp['home_team']['bookmaker']})",
            f"${opp['away_team']['ev']}",
            f"${opp['home_team']['ev']}"
        ]
        
        rows.append(row)
    
    print("\nArbitrage Opportunities:")
    print(tabulate(
        rows,
        headers=["Game", "Away Team (Odds @ Bookmaker)", "Home Team (Odds @ Bookmaker)", "Away EV", "Home EV"],
        tablefmt="grid"
    ))

def display_all_odds(game, team):
    """Display all odds for a specific team in a game"""
    all_odds = game.get_all_odds(team)
    
    if not all_odds:
        print(f"No odds found for {team}")
        return
    
    rows = []
    
    for odds_data in all_odds:
        implied_prob = EVCalculator.implied_probability(odds_data['odds'])
        ev = EVCalculator.calculate_ev(implied_prob, odds_data['odds'])
        
        row = [
            odds_data['bookmaker'],
            odds_data['odds'],
            f"{implied_prob:.2%}",
            f"${ev}"
        ]
        
        rows.append(row)
    
    # Sort by odds (highest first)
    rows.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\nAll Odds for {team}:")
    print(tabulate(
        rows,
        headers=["Bookmaker", "Odds", "Implied Probability", "EV"],
        tablefmt="grid"
    ))

def display_value_bets(value_bets, limit=10):
    """Display value bets in a table"""
    if not value_bets:
        print("\nNo positive expected value bets found")
        return
    
    # Limit the number of bets shown if there are many
    if limit and len(value_bets) > limit:
        bets_to_show = value_bets[:limit]
        print(f"\nTop {limit} Value Bets (out of {len(value_bets)} found):")
    else:
        bets_to_show = value_bets
        print(f"\nAll {len(value_bets)} Value Bets:")
    
    rows = []
    
    for i, bet in enumerate(bets_to_show, 1):
        # Format some values for display
        consensus_prob = f"{bet['consensus_probability']:.1%}"
        implied_prob = f"{bet['implied_probability']:.1%}"
        
        row = [
            i,  # Rank
            bet['game'],
            bet['team'],
            "Home" if bet['is_home'] else "Away",
            bet['bookmaker'],
            bet['odds'],
            f"{bet['edge']}% ({implied_prob} → {consensus_prob})",
            f"${bet['expected_value']} (per $100)"
        ]
        
        rows.append(row)
    
    print(tabulate(
        rows,
        headers=["Rank", "Game", "Team", "H/A", "Bookmaker", "Odds", "Edge", "Expected Value"],
        tablefmt="grid"
    ))

def display_all_bookmaker_odds(games):
    """Display all bookmaker odds for all games in a comprehensive table"""
    all_rows = []
    
    for game in games:
        game_time = game.commence_time.strftime("%Y-%m-%d %H:%M")
        
        # Get all odds for home team
        home_odds = game.get_all_odds(game.home_team)
        for odds_data in home_odds:
            row = [
                game_time,
                f"{game.away_team} @ {game.home_team}",
                game.home_team,
                "Home",
                odds_data['bookmaker'],
                odds_data['odds'],
                f"{(1/odds_data['odds']):.1%}"
            ]
            all_rows.append(row)
            
        # Get all odds for away team
        away_odds = game.get_all_odds(game.away_team)
        for odds_data in away_odds:
            row = [
                game_time,
                f"{game.away_team} @ {game.home_team}",
                game.away_team,
                "Away",
                odds_data['bookmaker'],
                odds_data['odds'],
                f"{(1/odds_data['odds']):.1%}"
            ]
            all_rows.append(row)
    
    # Sort by game time, then by game, then by team
    all_rows.sort(key=lambda x: (x[0], x[1], x[2]))
    
    print("\nAll Bookmaker Odds:")
    print(tabulate(
        all_rows,
        headers=["Game Time", "Game", "Team", "H/A", "Bookmaker", "Odds", "Implied Prob"],
        tablefmt="grid"
    ))

def main():
    parser = argparse.ArgumentParser(description="MLB Odds Finder")
    parser.add_argument("--show-all", action="store_true", help="Show all games, not just today's")
    parser.add_argument("--team", type=str, help="Show detailed odds for a specific team")
    parser.add_argument("--arbitrage", action="store_true", help="Find arbitrage opportunities")
    parser.add_argument("--value", action="store_true", help="Find positive expected value bets")
    parser.add_argument("--value-limit", type=int, default=10, help="Limit value bets shown (default: 10, 0 for all)")
    parser.add_argument("--min-odds", type=float, default=1.5, help="Minimum odds to consider for value bets")
    parser.add_argument("--max-odds", type=float, default=10.0, help="Maximum odds to consider for value bets")
    parser.add_argument("--date", type=str, help="Show games for a specific date (format: YYYY-MM-DD)")
    parser.add_argument("--all-odds", action="store_true", help="Show all odds from all bookmakers for all games")
    
    args = parser.parse_args()
    
    client = OddsApiClient()
    
    # Get MLB odds
    logger.info("Fetching MLB odds from the API")
    data = client.get_odds('baseball_mlb')
    
    if not data:
        logger.error("Failed to fetch odds data")
        return
    
    # Convert to our models
    games = [GameOdds.from_api(game_data) for game_data in data]
    logger.info(f"Fetched odds for {len(games)} MLB games")
    
    # Filter games by date if specified
    if args.date:
        try:
            # Parse the date string to a date object
            selected_date = datetime.strptime(args.date, "%Y-%m-%d").date()
            next_date = selected_date + timedelta(days=1)
            
            # Filter games for the selected date
            games = [
                game for game in games 
                if game.commence_time.date() >= selected_date and game.commence_time.date() < next_date
            ]
            logger.info(f"Filtered to {len(games)} games scheduled for {args.date}")
        except ValueError:
            logger.error(f"Invalid date format. Please use YYYY-MM-DD format.")
            return
    # Filter to today's games if not showing all and no specific date
    elif not args.show_all:
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        games = [
            game for game in games 
            if game.commence_time.date() >= today and game.commence_time.date() < tomorrow
        ]
        logger.info(f"Filtered to {len(games)} games scheduled for today")
    
    # Display results
    if args.all_odds:
        display_all_bookmaker_odds(games)
    elif args.team:
        # Find games with the specified team
        team_games = [game for game in games if args.team.lower() in game.home_team.lower() or args.team.lower() in game.away_team.lower()]
        
        if not team_games:
            print(f"No games found for team: {args.team}")
            return
        
        # Display all odds for the team in each game
        for game in team_games:
            if args.team.lower() in game.home_team.lower():
                team_name = game.home_team
            else:
                team_name = game.away_team
                
            print(f"\nGame: {game}")
            display_all_odds(game, team_name)
    elif args.arbitrage:
        # Find arbitrage opportunities
        opportunities = EVCalculator.find_arbitrage_opportunities(games)
        display_arbitrage(opportunities)
    elif args.value:
        # Find value bets
        value_bets = EVCalculator.find_best_value_bets(
            games, 
            min_odds=args.min_odds,
            max_odds=args.max_odds
        )
        display_value_bets(value_bets, limit=args.value_limit)
    else:
        # Display all games
        display_games(games)

if __name__ == "__main__":
    main() 