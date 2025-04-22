class EVCalculator:
    """Calculator for betting Expected Value"""
    
    @staticmethod
    def calculate_ev(win_probability, odds_decimal, bet_amount=100):
        """
        Calculate Expected Value
        
        Args:
            win_probability (float): Probability of winning (0-1)
            odds_decimal (float): Decimal odds offered by bookmaker
            bet_amount (float): Amount to bet
            
        Returns:
            float: Expected value
        """
        win_amount = (odds_decimal - 1) * bet_amount
        lose_amount = -bet_amount
        
        ev = (win_probability * win_amount) + ((1 - win_probability) * lose_amount)
        return round(ev, 2)
    
    @staticmethod
    def implied_probability(odds_decimal):
        """
        Calculate implied probability from decimal odds
        
        Args:
            odds_decimal (float): Decimal odds
            
        Returns:
            float: Implied probability (0-1)
        """
        return round(1 / odds_decimal, 4)
    
    @staticmethod
    def find_arbitrage_opportunities(games):
        """
        Find arbitrage opportunities from a collection of games
        
        Args:
            games (list): List of GameOdds objects
            
        Returns:
            list: List of arbitrage opportunities
        """
        opportunities = []
        
        for game in games:
            home_best = game.get_best_odds(game.home_team)
            away_best = game.get_best_odds(game.away_team)
            
            if not home_best['odds'] or not away_best['odds']:
                continue
            
            home_implied_prob = EVCalculator.implied_probability(home_best['odds'])
            away_implied_prob = EVCalculator.implied_probability(away_best['odds'])
            
            # Check for arbitrage (sum of probabilities < 1)
            if (home_implied_prob + away_implied_prob) < 0.98:
                # Calculate normalized probabilities
                total_prob = home_implied_prob + away_implied_prob
                home_true_prob = home_implied_prob / total_prob
                away_true_prob = away_implied_prob / total_prob
                
                # Calculate EV
                home_ev = EVCalculator.calculate_ev(home_true_prob, home_best['odds'])
                away_ev = EVCalculator.calculate_ev(away_true_prob, away_best['odds'])
                
                opportunity = {
                    'game': str(game),
                    'home_team': {
                        'name': game.home_team,
                        'best_odds': home_best['odds'],
                        'bookmaker': home_best['bookmaker'],
                        'implied_probability': home_implied_prob,
                        'true_probability': home_true_prob,
                        'ev': home_ev
                    },
                    'away_team': {
                        'name': game.away_team,
                        'best_odds': away_best['odds'],
                        'bookmaker': away_best['bookmaker'],
                        'implied_probability': away_implied_prob,
                        'true_probability': away_true_prob,
                        'ev': away_ev
                    }
                }
                
                opportunities.append(opportunity)
        
        return opportunities 
    
    @staticmethod
    def find_best_value_bets(games, min_odds=1.5, max_odds=10.0):
        """
        Find bets with positive expected value using market consensus as "true" probability
        
        Args:
            games (list): List of GameOdds objects
            min_odds (float): Minimum odds to consider
            max_odds (float): Maximum odds to consider
            
        Returns:
            list: List of value bets ranked by EV
        """
        value_bets = []
        
        for game in games:
            # Get all odds for each team
            home_odds_list = game.get_all_odds(game.home_team)
            away_odds_list = game.get_all_odds(game.away_team)
            
            if not home_odds_list or not away_odds_list:
                continue
            
            # Calculate consensus probabilities
            home_implied_probs = [1/odds['odds'] for odds in home_odds_list]
            away_implied_probs = [1/odds['odds'] for odds in away_odds_list]
            
            # Average the implied probabilities
            avg_home_implied = sum(home_implied_probs) / len(home_implied_probs)
            avg_away_implied = sum(away_implied_probs) / len(away_implied_probs)
            
            # Normalize to ensure they sum to 1
            total_prob = avg_home_implied + avg_away_implied
            home_true_prob = avg_home_implied / total_prob
            away_true_prob = avg_away_implied / total_prob
            
            # Check each bookmaker's odds for positive EV
            for odds_data in home_odds_list:
                odds = odds_data['odds']
                
                # Skip if outside of our preferred odds range
                if odds < min_odds or odds > max_odds:
                    continue
                    
                # Calculate EV using consensus probability
                ev = EVCalculator.calculate_ev(home_true_prob, odds)
                implied_prob = 1 / odds
                edge = (home_true_prob - implied_prob) * 100  # Edge percentage
                
                # Only include positive EV bets
                if ev > 0:
                    value_bets.append({
                        'game': str(game),
                        'team': game.home_team,
                        'is_home': True,
                        'odds': odds,
                        'bookmaker': odds_data['bookmaker'],
                        'implied_probability': implied_prob,
                        'consensus_probability': home_true_prob,
                        'edge': round(edge, 2),
                        'expected_value': ev
                    })
            
            # Do the same for away team
            for odds_data in away_odds_list:
                odds = odds_data['odds']
                
                # Skip if outside of our preferred odds range
                if odds < min_odds or odds > max_odds:
                    continue
                    
                ev = EVCalculator.calculate_ev(away_true_prob, odds)
                implied_prob = 1 / odds
                edge = (away_true_prob - implied_prob) * 100  # Edge percentage
                
                if ev > 0:
                    value_bets.append({
                        'game': str(game),
                        'team': game.away_team,
                        'is_home': False,
                        'odds': odds,
                        'bookmaker': odds_data['bookmaker'],
                        'implied_probability': implied_prob,
                        'consensus_probability': away_true_prob,
                        'edge': round(edge, 2),
                        'expected_value': ev
                    })
        
        # Rank by expected value (highest first)
        value_bets.sort(key=lambda x: x['expected_value'], reverse=True)
        
        return value_bets 