from datetime import datetime

class GameOdds:
    """Model representing odds for a single game"""
    
    def __init__(self, game_id, sport, commence_time, home_team, away_team, bookmakers=None):
        self.game_id = game_id
        self.sport = sport
        self.commence_time = commence_time
        self.home_team = home_team
        self.away_team = away_team
        self.bookmakers = bookmakers or []
        
    @classmethod
    def from_api(cls, api_data):
        """Create a GameOdds object from API data"""
        game_id = api_data.get('id')
        sport = api_data.get('sport_key')
        
        # Parse commence time
        commence_time_str = api_data.get('commence_time')
        commence_time = datetime.fromisoformat(commence_time_str.replace('Z', '+00:00'))
        
        # Get teams
        home_team = api_data.get('home_team')
        away_team = api_data.get('away_team')
        
        # Create instance
        game_odds = cls(game_id, sport, commence_time, home_team, away_team)
        
        # Add bookmakers
        for bm_data in api_data.get('bookmakers', []):
            bookmaker = Bookmaker.from_api(bm_data)
            game_odds.bookmakers.append(bookmaker)
            
        return game_odds
    
    def get_best_odds(self, team):
        """Get the best (highest) odds for a team across all bookmakers"""
        best_odds = 0
        best_bookmaker = None
        
        for bookmaker in self.bookmakers:
            for market in bookmaker.markets:
                if market.market_type == 'h2h':
                    for outcome in market.outcomes:
                        if outcome.name == team and outcome.price > best_odds:
                            best_odds = outcome.price
                            best_bookmaker = bookmaker.title
        
        return {
            'odds': best_odds,
            'bookmaker': best_bookmaker
        }
        
    def get_all_odds(self, team):
        """Get all odds for a team across all bookmakers"""
        all_odds = []
        
        for bookmaker in self.bookmakers:
            for market in bookmaker.markets:
                if market.market_type == 'h2h':
                    for outcome in market.outcomes:
                        if outcome.name == team:
                            all_odds.append({
                                'bookmaker': bookmaker.title,
                                'odds': outcome.price
                            })
        
        return all_odds
    
    def __str__(self):
        return f"{self.away_team} @ {self.home_team} ({self.commence_time.strftime('%Y-%m-%d %H:%M')})"

class Bookmaker:
    """Model representing a bookmaker with odds"""
    
    def __init__(self, key, title, last_update, markets=None):
        self.key = key
        self.title = title
        self.last_update = last_update
        self.markets = markets or []
        
    @classmethod
    def from_api(cls, api_data):
        """Create a Bookmaker object from API data"""
        key = api_data.get('key')
        title = api_data.get('title')
        
        # Parse last update time
        last_update_str = api_data.get('last_update')
        last_update = datetime.fromisoformat(last_update_str.replace('Z', '+00:00'))
        
        # Create instance
        bookmaker = cls(key, title, last_update)
        
        # Add markets
        for market_data in api_data.get('markets', []):
            market = Market.from_api(market_data)
            bookmaker.markets.append(market)
            
        return bookmaker

class Market:
    """Model representing a betting market (e.g., h2h, spreads)"""
    
    def __init__(self, market_type, outcomes=None):
        self.market_type = market_type
        self.outcomes = outcomes or []
        
    @classmethod
    def from_api(cls, api_data):
        """Create a Market object from API data"""
        market_type = api_data.get('key')
        
        # Create instance
        market = cls(market_type)
        
        # Add outcomes
        for outcome_data in api_data.get('outcomes', []):
            outcome = Outcome.from_api(outcome_data)
            market.outcomes.append(outcome)
            
        return market

class Outcome:
    """Model representing an outcome in a betting market"""
    
    def __init__(self, name, price, point=None):
        self.name = name
        self.price = price  # Decimal odds
        self.point = point  # For spreads and totals
        
    @classmethod
    def from_api(cls, api_data):
        """Create an Outcome object from API data"""
        name = api_data.get('name')
        price = api_data.get('price')
        point = api_data.get('point')
        
        return cls(name, price, point) 