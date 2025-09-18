import numpy as np
import pandas as pd

from scipy.stats import binomtest

from sklearn.cluster import AgglomerativeClustering


def generate_archetypes(X, cards_data, vocabulary, n_cards=4, remove_pct=1):

    # Most other uses need the vocabulary, we need the inverse here though.
    #
    vocabulary_inv = {v:k for k, v in vocabulary.items() if k is not None}

    # Control granularity with distance_threshold or n_clusters
    agg_clustering = AgglomerativeClustering(
        n_clusters=None, 
        distance_threshold=60,  # Adjust this for granularity
        metric='manhattan',
        linkage='single'
    )
    cluster_labels_raw = agg_clustering.fit_predict(X.toarray()).astype(str)
    del agg_clustering


    unique_values, counts = np.unique(cluster_labels_raw, return_counts=True)
    to_remove = unique_values[counts<X.shape[0]*remove_pct/100] # Remove decks with <remove_pct%

    deck_archetypes = cluster_labels_raw
    deck_archetypes[np.isin(cluster_labels_raw, to_remove)] = '-1'

    unique_values, counts = np.unique(deck_archetypes, return_counts=True)
    clusters_count, clusters_id = zip(*sorted(zip(counts, unique_values), reverse=True))

    cluster_map = {'-1':'Other'}

    overall_means = np.array(X.mean(axis=0)).flatten()

    for i in clusters_id:
        if i != '-1':
            cluster_mask = deck_archetypes == i
            cluster_decks = X[cluster_mask]
            cluster_decks.data = np.clip(cluster_decks.data, 0, 4)
            card_frequencies = np.array((cluster_decks > 0).mean(axis=0)).flatten() # Proportion of decks playing each card
            weighted_scores = np.array(cluster_decks.mean(axis=0)).flatten() * card_frequencies

            cluster_means = np.array(cluster_decks.mean(axis=0)).flatten()
            

            # Apply land penalty if needed
            land_penalty = np.array(
                [
                    0.5 if 'Land' in cards_data.get(
                        vocabulary_inv.get(idx).replace('_SB',''),[{'types':[]}]
                    )[0]['types'] else 1.0 for idx in range(X.shape[1])
                ]
            )
            card_frequencies *= land_penalty
            distinctiveness = (cluster_means / (overall_means + 1e-8)) * land_penalty

            combined_scores = weighted_scores * distinctiveness

            # Get sorted indices for each category
            representative = np.argsort(combined_scores)[::-1][:n_cards]

            cluster_map[i] = '\n'.join([vocabulary_inv.get(a).replace('_SB','') for a in representative])
            # cluster_map[i] = make_card_stack([vocabulary_inv.get(a).replace('_SB','') for a in representative], cards_data)

    archetype_list = list(map(cluster_map.get, list(clusters_id)))
    return cluster_map, clusters_id, archetype_list, deck_archetypes

def make_matchup_matrix(df, res_df, cluster_map, clusters_id, archetype_list):

    res_arch = pd.merge(
        res_df, df[['Player', 'Tournament', 'Archetype']], 
        left_on=['Player1', 'Tournament'], right_on=['Player', 'Tournament'],
    )
    res_arch = pd.merge(
        res_arch, df[['Player', 'Tournament', 'Archetype']], 
        left_on=['Player2', 'Tournament'], right_on=['Player', 'Tournament'], 
        suffixes = ('_W','_L')
    )

    # TODO There is a bug here if we end up with an archetype that doesn't have any valid matches played against others.
    # Win counts matrix (W vs L)
    #
    df_wins = pd.crosstab(
        res_arch['Archetype_W'], res_arch['Archetype_L'], margins=False
    ).reindex(
        list(clusters_id)
    ).rename(
        columns=cluster_map, index=cluster_map
    )[
        archetype_list
    ]

    # Loss counts matrix (L vs W) - transpose the matchup
    df_losses = pd.crosstab(
        res_arch['Archetype_L'], res_arch['Archetype_W'], margins=False
    ).reindex(
        list(clusters_id)
    ).rename(
        columns=cluster_map, index=cluster_map
    )[
        archetype_list
    ]

    # Combine for total games and win percentages
    df_matches = df_wins.add(df_losses, fill_value=0)
    df_winrates = df_wins.div(df_matches, fill_value=0)

    # --- Prepare long-form winrate + match count ---
    # df_wr_long = df_winrates.reset_index().melt(id_vars='Archetype_W', var_name='Opponent', value_name='WinRate')
    # df_wr_long.rename(columns={'Archetype_W': 'Archetype'}, inplace=True)

    # df_mc_long = df_matches.reset_index().melt(id_vars='Archetype_W', var_name='Opponent', value_name='MatchCount')
    # df_mc_long.rename(columns={'Archetype_W': 'Archetype'}, inplace=True)

    # df_merged = pd.merge(df_wr_long, df_mc_long, on=['Archetype', 'Opponent'])
    # df_merged.dropna(subset=['WinRate'], inplace=True)

    # --- Aggregate wins and matches ---
    archetype_wins = (df_winrates * df_matches).sum(axis=1)
    archetype_matches = df_matches.sum(axis=1)

    # --- Compute win rates ---
    # win_rates = (archetype_wins / archetype_matches).reindex(sorted_archetypes)
    # match_counts = archetype_matches.reindex(sorted_archetypes).astype(int)

    # --- Compute binomial confidence intervals ---
    ci_data = []
    for archetype in archetype_list:
        wins = archetype_wins.get(archetype, 0)
        total = archetype_matches.get(archetype, 0)

        if total > 0:
            ci = binomtest(int(round(wins)), n=total).proportion_ci(confidence_level=0.95)
            win_rate = wins / total
            ci_data.append((win_rate, archetype, win_rate - ci.low, ci.high - win_rate))
        else:
            ci_data.append((np.nan, archetype, np.nan, np.nan))

    return ci_data, df_winrates
