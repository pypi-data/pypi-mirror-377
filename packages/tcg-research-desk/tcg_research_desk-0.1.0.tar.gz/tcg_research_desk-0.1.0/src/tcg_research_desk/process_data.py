# process_data.py
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
import json
from pathlib import Path
from datetime import datetime, timedelta

from scipy import sparse

from .utils import fuzzy_join


def get_tournament_files(base_path='../MTG_decklistcache/Tournaments', lookback_days=365, fmt='modern'):
    """
    Find all modern tournament files from the last lookback_days.
    
    Parameters:
    -----------
    base_path : str
        Path to tournament data directory
    lookback_days : int
        Number of days to look back
    fmt : str
        Tournament format
        
    Returns:
    --------
    list
        List of Path objects for matching tournament files
    """
    cutoff_date = datetime.now() - timedelta(days=lookback_days)
    
    # Get all possible year/month/day combinations from cutoff to now
    date_range = []
    current_date = cutoff_date
    while current_date <= datetime.now():
        date_range.append(current_date)
        current_date += timedelta(days=1)
    
    # Create patterns for each date
    # TODO Remove pre-modern and premodern from modern
    #
    patterns = [
        f"*/{date.year}/{date.month:02d}/{date.day:02d}/*-{fmt}*.json"
        for date in date_range
    ]
    
    # Find all matching files
    matching_files = []
    base_path = Path(base_path)
    for pattern in patterns:
        matching_files.extend(base_path.glob(pattern))

    if not matching_files:
        raise ValueError('No valid file paths were found.')
    
    return matching_files

def process_mtg_data(lookback_days=182, fmt='Modern'):
    """Process MTG tournament data and save results for dashboard consumption."""

    print(f'Processing {fmt} tournament files')

    # Initialize empty DataFrame to store all tournament data,
    # And one to store match results.
    #
    df = pd.DataFrame()
    res_df = pd.DataFrame()
    
    # Process tournament files
    tournament_path = Path('../MTG_decklistcache/Tournaments/')
    # Add tqdm back here if needed.
    for path in get_tournament_files(tournament_path, lookback_days, fmt.lower()):
        try:
            with open(path) as f:
                data = json.load(f)
            
            deck_df = pd.DataFrame(data['Decks'])
            deck_df['Deck'] = data['Decks']
            deck_df['Tournament'] = path.name
            standings_df = pd.DataFrame(data['Standings'])

            # Process matches for matchup matrix.
            #
            if data['Rounds'] is not None and len(data['Rounds']):
                round_df = pd.concat([pd.DataFrame(r['Matches']) for r in data['Rounds']], ignore_index=True)

                # Some players we don't have deck lists for, so we shouldn't include them in the wr.
                #
                round_df = round_df[
                    round_df['Player1'].isin(deck_df['Player']) & round_df['Player2'].isin(deck_df['Player'])
                ]

                if round_df.shape[0]:

                    round_df[['gW', 'gL', 'gD']] = round_df['Result'].str.split('-', expand=True).astype(int)

                    round_df['Date'] = f'{path.parent.parent.parent.name}-{path.parent.parent.name}-{path.parent.name}'
                    round_df['Tournament'] = path.name

                    res_df = pd.concat([
                        res_df, 
                        round_df[round_df['gW'] == 2][
                            ['Date','Tournament','Player1','Player2']
                        ]
                    ], ignore_index=True)
            
            # Process standings for overall wr.
            #
            if standings_df.shape[0]:
                if deck_df.loc[0, 'Result'].endswith('Place'):
                    deck_df['Rank'] = deck_df['Result'].str[:-8].astype(int)
                else:
                    deck_df['Rank'] = range(deck_df.shape[0])
                deck_df = fuzzy_join(deck_df, standings_df)

                if deck_df['Wins'].sum() == deck_df['Losses'].sum():
                    # Everything is fine.
                    #
                    deck_df['Invalid_WR'] = False
                # TODO: Need to fix the below, currently melee doesn't have round results.
                elif data['Rounds'] is not None and len(data['Rounds']):
                    # We need to build the win rates from the individual rounds.
                    # To do so we'll use the round_df from above.
                    #
                    
                    for i in deck_df.index:
                        # In order, 
                        # Make sure our player won/lost,
                        # Make sure it wasn't a draw,
                        # Make sure it wasn't a bye.
                        deck_df.loc[i, 'Wins'] = (
                            (round_df['Player1'] == deck_df.loc[i, 'Player']) & \
                            round_df['Result'].str.startswith('2') & \
                            ~(round_df['Player2'] == ('-'))
                        ).sum(axis=None)
                        deck_df.loc[i, 'Losses'] = (
                            (round_df['Player2'] == deck_df.loc[i, 'Player']) & \
                            round_df['Result'].str.startswith('2')
                        ).sum(axis=None)
                    
                    if deck_df['Wins'].sum() == deck_df['Losses'].sum():
                        # Everything is fine.
                        #
                        deck_df['Invalid_WR'] = False
                    else:
                        deck_df['Invalid_WR'] = True
                        # print(deck_df['Player'].nunique(), deck_df.shape)
                        # print(path, deck_df['Wins'].sum(), deck_df['Losses'].sum())
                        print(f'Could not fix {path}')

                elif 'mtgo.com' in str(path):
                    # Draws can't happen, we can look at points.
                    # Sometimes wins aren't recorded.
                    # Could be the same for losses, but we can't do anything about that.
                    # We'll fix for wins and if things are still broken call it.
                    #
                    deck_df['Wins'] = deck_df['Points'] / 3

                    if deck_df['Wins'].sum() == deck_df['Losses'].sum():
                        # Everything is fine.
                        #
                        deck_df['Invalid_WR'] = False
                    else:
                        deck_df['Invalid_WR'] = True
                        # print(deck_df['Player'].nunique(), deck_df.shape)
                        # print(path, deck_df['Wins'].sum(), deck_df['Losses'].sum())
                        print(f'Could not fix mtgo event {path}')

                else:
                    deck_df['Invalid_WR'] = True
            else:
                deck_df['Invalid_WR'] = True

            
            # Set date from path if missing
            deck_df['Date'] = f'{path.parent.parent.parent.name}-{path.parent.parent.name}-{path.parent.name}'
            limited_cols = [
                c for c in ['Deck', 'Player', 'Wins', 'Losses', 'Date', 'Tournament', 'Invalid_WR'] if c in deck_df.columns
            ]
            df = pd.concat([df, deck_df[limited_cols]], ignore_index=True)
        except Exception as e:
            print(path)
            raise e
        
    if not df.shape[0]:
        raise ValueError('No data was found in the specified files.')
    
    # Convert dates and sort
    #
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by='Date')

    df = df.dropna(subset=['Date','Deck'])

    print(f'deck data loaded, shape={df.shape}')
    print(f'Invalid win rates: shape=({df["Invalid_WR"].sum()})')

    # Load card data
    #
    with open('../AtomicCards.json', 'r') as f:
        j = json.load(f)['data']

    # Oracle Id look up for card hovering.
    #
    oracleid_lookup = dict()
    for k, v in list(j.items()):
        if not v[0].get('isFunny'):
            # Handle for overloaded card names.
            #
            if v[0].get('name') not in ['Pick Your Poison', 'Red Herring', 'Unquenchable Fury']:
                oracleid_lookup[k] = v[0]['identifiers']['scryfallOracleId']
                
                # If we have a split card, also add the front name for robust behavior
                if '//' in k:
                    oracleid_lookup[k.split('//')[0].strip()] = v[0]['identifiers']['scryfallOracleId']
            else:
                for face in v:
                    if 'vintage' in face['legalities'].keys() and not face.get('isFunny'):
                        oracleid_lookup[k] = face['identifiers']['scryfallOracleId']

    
    # Vectorize decks
    def merge_analyzer(deck):
        """Convert deck dictionary into list of card strings."""
        output = []
        for card in deck['Mainboard']:
            # if card['CardName'] in card_list:
            #     if 'Land' not in j[card['CardName']][0]['type']:
            #         output += [card['CardName']] * card['Count']
            # else:
            output += [card['CardName']] * card['Count']
        for card in deck['Sideboard']:
            output += [card['CardName']+'_SB'] * card['Count']
        return output

    vectorizer = CountVectorizer(analyzer=merge_analyzer)
    X = vectorizer.fit_transform(df['Deck'])
    
    # Apply Information Weight Transform
    # iwt = InformationWeightTransformer()
    # X_iwt = iwt.fit_transform(X)

    print('Vectorized')
    
    # Create output directory
    Path('processed_data').mkdir(exist_ok=True)

    # Generate and save metadata
    metadata = {
        'last_updated': datetime.utcnow().isoformat(),
        'num_decks': df.shape[0],
        'date_range': [df['Date'].min().isoformat(), df['Date'].max().isoformat()],
    }
    
    with open(f'processed_data/metadata.json', 'w') as f:
        json.dump(metadata, f)
    
    df['Date'] = df['Date'].astype(str)
    # Save processed data
    output_data = {
        'decks': df[['Player', 'Wins', 'Losses', 'Date', 'Tournament', 'Invalid_WR']].to_dict('records'),
        'results': res_df.to_dict('records'),
        'cluster_info': [],
        'feature_names': vectorizer.get_feature_names_out().tolist()
    }
    
    with open(f'processed_data/deck_data.json', 'w') as f:
        json.dump(output_data, f)

    with open(f'processed_data/card_data.json', 'w') as f:
        json.dump(oracleid_lookup, f)
    
    # Save matrices
    sparse.save_npz(f'processed_data/card_vectors.npz', X)
    
    # Save transformers data
    vectorizer_data = {
        'vocabulary': vectorizer.vocabulary_
    }
    with open(f'processed_data/vectorizer.json', 'w') as f:
        json.dump(vectorizer_data, f)

    print('Data saved, done')

# Load and process data
def load_data(data_path='processed_data', lookback_days=365):
    """
    Load preprocessed MTG tournament data for dashboard visualization.
    
    Parameters:
    -----------
    data_path : str
        Path to the directory containing processed data files
    lookback_days : int
        Number of days of data to load (to avoid loading entire history)
        
    Returns:
    --------
    tuple
        (
            DataFrame with deck data, 
            sparse matrix of card counts, 
            fitted CountVectorizer vocabulary,
            dictionary for oracleid lookups,
        )
    """
    # Load the preprocessed data
    with open(Path(data_path) / 'deck_data.json', 'r') as f:
        data = json.load(f)
        
    # Convert to DataFrame
    df = pd.DataFrame(data['decks'])
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    
    res_df = pd.DataFrame(data['results'])

    # Filter to recent data
    cutoff_date = (pd.to_datetime('today') - pd.Timedelta(days=lookback_days)).date()

    # Load card vectors
    X = sparse.load_npz(Path(data_path) / 'card_vectors.npz')[(df['Date'] >= cutoff_date).to_list()]

    df = df[df['Date'] >= cutoff_date].reset_index()
    
    # Load and reconstruct vectorizer
    with open(Path(data_path) / 'vectorizer.json', 'r') as f:
        vectorizer_data = json.load(f)

    # Load oracleid lookup
    with open(Path(data_path) / 'card_data.json', 'r') as f:
        oracleid_lookup = json.load(f)
    
    # vectorizer = CountVectorizer()
    # vectorizer.vocabulary_ = vectorizer_data['vocabulary']
    # vectorizer.fixed_vocabulary_ = True
    
    return df, X, res_df, vectorizer_data['vocabulary'], oracleid_lookup

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("format", help="Format to process", default='Modern')
    args = parser.parse_args()

    process_mtg_data(fmt=args.format)#lookback_days=30)
