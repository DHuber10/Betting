import requests
from .config import API_KEY, API_BASE_URL, REGIONS, MARKETS, ODDS_FORMAT, DATE_FORMAT
import logging

logger = logging.getLogger(__name__)

class OddsApiClient:
    """Client for accessing the Odds API"""
    
    def __init__(self, api_key=API_KEY):
        self.api_key = api_key
        self.base_url = API_BASE_URL
        
    def get_sports(self):
        """Get a list of available sports"""
        url = f"{self.base_url}/sports"
        
        response = requests.get(
            url,
            params={
                'api_key': self.api_key
            }
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to get sports: status_code {response.status_code}, response body {response.text}")
            return None
            
        return response.json()
        
    def get_odds(self, sport='baseball_mlb'):
        """Get odds for a specific sport"""
        url = f"{self.base_url}/sports/{sport}/odds"
        
        response = requests.get(
            url,
            params={
                'api_key': self.api_key,
                'regions': REGIONS,
                'markets': MARKETS,
                'oddsFormat': ODDS_FORMAT,
                'dateFormat': DATE_FORMAT,
            }
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to get odds: status_code {response.status_code}, response body {response.text}")
            return None
            
        # Log API usage
        requests_remaining = response.headers.get('x-requests-remaining', 'unknown')
        requests_used = response.headers.get('x-requests-used', 'unknown')
        
        logger.info(f"API usage - Remaining requests: {requests_remaining}, Used requests: {requests_used}")
        
        return response.json() 