from numpy import isnan

# Color mappings for mana symbols and backgrounds
COLOR_MAP_FACE = {
    'W': '#f7f8f4', 
    'U': '#c4cde5', 
    'B': '#c1b9be', 
    'R': '#e5cdba', 
    'G': '#bfcfc7',
    'Multi': '#d4c28a',
    'Artifact': '#babcbb',
    'Colorless': '#d6d5d4',
    'Land': '#d6d5d4',
}

COLOR_MAP_PIPING = {
    'W': '#eeeef2', 
    'U': '#2e61b6', 
    'B': '#3f433b', 
    'R': '#c45135', 
    'G': '#317246',
    'Multi': '#e3d376',
    'Artifact': '#d6d5d4',
    'Colorless': '#d6d5d4',
    'Land': '#9e9282',
}

def make_card_html(card_name, mtgjson_data, fix_width=False, show_mana=True, font_size='7px'):
    card_info = mtgjson_data.get(card_name, [{}])[0]
    mana_cost = card_info.get('manaCost', '')
    colors = card_info.get('colors', [])
    types = card_info.get('types', [])

    # https://mana.andrewgioia.com/index.html

    if mana_cost and show_mana:
        # <i class="ms ms-cost ms-g"></i>
        mana_cost = ''.join([
            '<i class="ms ms-' + ''.join(s.split('/')).lower() + ' ms-cost ms-shadow"></i>' for s in mana_cost[1:-1].split('}{')
        ])

    mana = f'<div style="display: flex; align-items: center; color: #000;">{mana_cost}</div>' if show_mana else ''

    piping = 2  # px
    inner_radius_x, inner_radius_y = 9, 20
    outer_radius_x, outer_radius_y = inner_radius_x + piping, inner_radius_y + piping

    # Base style decisions
    if 'Artifact' in types and not colors:
        frame_color = COLOR_MAP_FACE['Artifact']
        border_color_1 = COLOR_MAP_PIPING['Artifact']
        border_color_2 = COLOR_MAP_PIPING['Artifact']
    elif 'Land' in types and not colors:
        frame_color = COLOR_MAP_FACE['Land']
        border_color_1 = COLOR_MAP_PIPING['Land']
        border_color_2 = COLOR_MAP_PIPING['Land']
    elif len(colors) == 0:
        frame_color = COLOR_MAP_FACE['Colorless']
        border_color_1 = COLOR_MAP_PIPING['Colorless']
        border_color_2 = COLOR_MAP_PIPING['Colorless']
    elif len(colors) == 1:
        frame_color = COLOR_MAP_FACE[colors[0]]
        border_color_1 = COLOR_MAP_PIPING[colors[0]]
        border_color_2 = COLOR_MAP_PIPING[colors[0]]
    elif len(colors) == 2:
        c1, c2 = colors[0], colors[1]
        frame_color = COLOR_MAP_FACE['Multi']
        border_color_1 = COLOR_MAP_PIPING[c1]
        border_color_2 = COLOR_MAP_PIPING[c2]
        
    else:
        # 3+ colors (fallback to your existing "Multi" solid piping)
        frame_color = COLOR_MAP_FACE['Multi']
        border_color_1 = COLOR_MAP_PIPING['Multi']
        border_color_2 = COLOR_MAP_PIPING['Multi']

    gradient_css = f"linear-gradient(to right, {border_color_2}, {border_color_1})"

    width_str = f'width: {fix_width}px;' if fix_width else ''

    return f"""
    <div style="
        background: {gradient_css};
        padding: {piping}px;
        border-radius: {outer_radius_x}px/{outer_radius_y}px;
        display: inline-flex; {width_str}
        box-sizing: border-box;
        box-shadow: -1px 1px 1px 1px #171314;
    ">
    <div style="
        background: {frame_color};
        box-shadow: 0 0 0 1px #171314;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0px 2px;
        border-radius: {inner_radius_x}px/{inner_radius_y}px;
        font-family: 'Trebuchet MS', sans-serif;
        min-width: 30px;
        font-size: {font_size};
        width: 100%;
        max-width: 100%;
        box-sizing: border-box;
    ">
        <div style="
            font-weight: 600;
            color: #000;
            flex-grow: 1;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            font-size: clamp(4px, 1vw, {font_size});
        ">{card_name}</div>
        {mana}
    </div>
    </div>
    """

def make_card_stack(card_names, mtgjson_data, fix_width=False, show_mana=True, font_size='7px'):
    num_cards = len(card_names)
    width = f'width: {fix_width}px;' if fix_width else 'width:100%; max-width:100%; box-sizing:border-box;'
    stack = ''.join([
        make_card_html(
            card, 
            mtgjson_data, 
            fix_width=fix_width, 
            show_mana=show_mana, 
            font_size=font_size
        ) for card in card_names
    ])

    if num_cards != 1:
        
        return f"""
    <div style="
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        grid-template-rows: repeat(2, auto);
        gap: 2px;
        {width}
    ">
        {stack}
    </div>
    """.replace('\n','')
            
    else:
        return f"""    
    <div style="
        display: grid;
        grid-template-columns: 1fr;
        {width}
    ">
        {stack}
    </div>
    """.replace('\n','')

def make_matchup_matrix(
    archetypes, matchups,
    cards_data,
    cell_size=40, row_height=40,
    levels=4, vertical_spacing=35, label_width=60
):
    """
    Create a matchup matrix with horizontal card-stack headers at multiple vertical levels.

    Parameters
    ----------
    archetypes : list[str] - column/row archetypes
    matchups : dict[(str,str) -> float] - win rates
    cell_size : int - width/height of matrix cell
    row_height : int - height of matrix row
    make_card_stack : callable - generates card stack HTML
    cards_data : dict - card metadata
    levels : int - number of vertical levels to stagger headers
    vertical_spacing : int - px between levels

    Returns
    -------
    HTML string for the matrix, header height
    """
    header_row_height = int(vertical_spacing * (levels+0.25))

    # Build labels and dashed lines together.
    dotted_lines = []
    header_labels = []

    for i, col_arch in enumerate(archetypes):
        card_list = col_arch.split("\n")
        card_stack_html = make_card_stack(card_list, cards_data, fix_width=label_width, show_mana=False)

        # stagger the vertical position in a repeating pattern
        level = i % levels
        top_offset = level * vertical_spacing

        header_labels.append(f'''
        <div style="
            position:absolute;
            top:{top_offset}px;
            left:{cell_size * (i-1) + (cell_size-label_width) // 2}px;
            transform: translateX(-50%);
            z-index:1;
        ">
            {card_stack_html}
        </div>
        ''')

        dotted_lines.append(f'''
        <div style="
            position:absolute;
            top:{top_offset + 0.5*vertical_spacing}px;
            left:{cell_size * i + cell_size // 2}px;
            width:2px;
            height:{(levels-0.5 - level+0.25) * vertical_spacing}px;
            border-left:2px solid #999;
            z-index:0;
            transform: translateX(-50%);
        "></div>
        ''')

    dotted_lines_html = f'''
    <div style="position:absolute; top:0; left:0; width:100%; height:{header_row_height + row_height}px; z-index:0;">
        {''.join(dotted_lines)}
    </div>
    '''

    header_labels_html = f'''
    <div style="position:relative; height:{header_row_height}px; margin-left:{cell_size}px; z-index:1;">
        {''.join(header_labels)}
    </div>
    '''

    # --- Body rows ---
    body_rows_html = []
    for row_arch in archetypes:
        row_cells = []
        for col_arch in archetypes:
            wr = matchups.loc[row_arch, col_arch]
            if isnan(wr):
                bg_color = "#eee"
                cell_content = ""
            else:
                red = int(255 * min(1, 2 - wr*2))
                green = int(255 * min(1, wr*2))
                blue = int(255 * min(2 - wr*2, wr*2))
                bg_color = f"rgb({red},{green},{blue})"
                cell_content = f"{wr:.1%}"

            row_cells.append(f'''
                <div style="
                    width:{cell_size}px;
                    height:{row_height}px;
                    background:{bg_color};
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:10px;
                    border:1px solid #ccc;
                    box-sizing:border-box;
                ">{cell_content}</div>
            ''')
        body_rows_html.append(
            '<div style="display:flex;">' + "".join(row_cells) + '</div>'
        )

    matrix_html = (
        '<div class="matchup-matrix" style="display:inline-block; vertical-align:top; position:relative;">'
        + dotted_lines_html
        + header_labels_html
        + "".join(body_rows_html)
        + '</div>'
    )

    return matrix_html, header_row_height

def make_combined_matchup_html(
    ci_data,                 # list of (win_rate, archetype, err_low, err_high)
    sorted_archetypes,       # list of archetype names (top -> bottom)
    matchups,                # dataframe with matchups 
    cards_data,              # whatever your make_card_stack needs
    plot_width=600,          # px
    labels_width=280,        # px: fixed width for the left column
    row_height=40,           # px per row
    xticks=(0.0, 0.25, 0.5, 0.75, 1.0),
    top_margin=0,
):
    # Make the matrix first to get header height.
    matrix_html, top_margin = make_matchup_matrix(sorted_archetypes, matchups, cards_data, levels=4)

    # LEFT COLUMN: fixed width; each row forces its content to width:100%
    left_rows = []
    for a in sorted_archetypes:
        stack = make_card_stack(a.split('\n'), cards_data)
        left_rows.append(
            # Row container (fixed height/width)
            f"<div style='height:{row_height}px; width:{labels_width}px; "
            f"display:flex; align-items:center;'>"
            # IMPORTANT: ensure your card element does NOT have min-width; use width:100% in its style
            f"{stack}"
            "</div>"
        )
    labels_col_html = f"<div style='margin-top:{top_margin}px; position:relative;'>" + "".join(left_rows) + "</div>"

    # RIGHT COLUMN: scatter + error bars (absolute positioning)
    plot_height = len(sorted_archetypes) * row_height
    arch_to_row = {a: i for i, a in enumerate(sorted_archetypes)}

    scatter_items = []

    # Vertical grid lines at xticks
    for x in xticks:
        if x != 0.5:
            x_pct = x * 100
            scatter_items.append(
                f'<div style="position:absolute; left:{x_pct}%; top:0; '
                f'width:1px; height:100%; background:#eee;"></div>'
            )

        else:
            # Reference line at 0.5
            scatter_items.append(
                '<div style="position:absolute; left:50%; top:0; '
                'width:1px; height:100%; border-left: 2px dashed red;"></div>'
            )

    # Points + error bars (centered vertically in each row)
    for wr, archetype, err_low, err_high in ci_data:
        if archetype not in arch_to_row or wr is None:
            continue
        row_idx = arch_to_row[archetype]
        center_y = row_idx * row_height + row_height / 2

        left_pct = (wr - err_low) * 100
        right_pct = (wr + err_high) * 100
        center_pct = wr * 100

        # Error bar
        scatter_items.append(
            f'<div style="position:absolute; left:{left_pct}%; '
            f'top:{center_y-1}px; width:{right_pct-left_pct}%; height:2px; '
            'background:black;"></div>'
        )
        # Point
        scatter_items.append(
            f'<div style="position:absolute; left:calc({center_pct}% - 4px); '
            f'top:{center_y-4}px; width:8px; height:8px; '
            'background:black; border-radius:50%;"></div>'
        )

    scatter_col_html = (
        f'<div style="position:relative; width:{plot_width}px; height:{plot_height}px; '
        f'border-left:1px solid #ccc; box-sizing:border-box; margin-top:{top_margin}px;">'
        + "".join(scatter_items) +
        '</div>'
    )

    # X-axis labels: absolutely centered on each grid line
    tick_labels = []
    for x in xticks:
        x_pct = x * 100
        tick_labels.append(
            f'<div style="position:absolute; left:{x_pct}%;'
            f'top:0; white-space:nowrap; font-size:12px;">{int(round(x*100))}%</div>'
        )
    x_axis_html = (
        f'<div style="position:relative; width:{plot_width}px; height:18px; '
        # f'margin-left:{labels_width}px;'
        'margin-top:4px;">'
        + "".join(tick_labels) +
        '</div>'
    )

    # Combined grid: fixed left column + fixed right plot
    # Mana symbols from:
    # https://mana.andrewgioia.com/index.html
    #
    combined = (
        '<link href="//cdn.jsdelivr.net/npm/mana-font@latest/css/mana.css" rel="stylesheet" type="text/css" />'
        f'<div style="display:grid; grid-template-columns: {plot_width}px {labels_width}px 1fr; '
        f'column-gap:10px; align-items:start;">'
        f'{scatter_col_html}'
        f'{labels_col_html}'
        f'{matrix_html}'
        '</div>'
        f'{x_axis_html}'
    )
    return combined
