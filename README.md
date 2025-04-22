-- Commands to run app

-- Install dependencies
pip3 install -e .

-- To see all odss for a day
python3 mlb_odds.main --date 2025-04-22 --all-odds

-- To see the positive EV odds for a day
python3 -m mlb_odds.main --value --date 2025-04-22
