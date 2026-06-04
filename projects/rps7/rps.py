from nicegui import ui, app
from pathlib import Path

import uuid
import random
import yaml
import time


PROJECTS_DIR = Path(__file__).parent / ""

# Game state: keyed by game code
current_games = {}

MOVE_ICONS = {
    'Rock': '🪨', 'Paper': '📄', 'Scissors': '✂️', 'Lizard': '🦎',
    'Spock': '🖖', 'Fire': '🔥', 'Water': '💧', 'Air': '💨',
    'Dragon': '🐉', 'Devil': '😈', 'Lightning': '⚡', 'Gun': '🔫',
    'Snake': '🐍', 'Human': '🧑', 'Tree': '🌳', 'Wolf': '🐺', 'Sponge': '🧽',
}


def get_icon(move):
    return MOVE_ICONS.get(move, '❓')


def load_from_yaml():
    """
    Parse seven.yaml to extract:
      - MOVE_LIST: ordered list of move names (series > data > name)
      - MOVE_COLORS: {name: hex color} (series > data > itemStyle > color)
      - WIN_MAP: {name: [names it beats]} (series > links, source beats target)
    Falls back to sensible defaults if the file isn't found.
    """
    yaml_path = Path(f'{PROJECTS_DIR}/seven.yaml')
    if yaml_path.exists():
        data = yaml.safe_load(yaml_path.read_text())
        series = data.get('series', {})
        nodes = series.get('data', [])
        links = series.get('links', [])

        move_list = [n['name'] for n in nodes]
        move_colors = {n['name']: n.get('itemStyle', {}).get('color', '#888888') for n in nodes}

        win_map = {name: [] for name in move_list}
        for link in links:
            src = link.get('source')
            tgt = link.get('target')
            if src in win_map:
                win_map[src].append(tgt)

        return move_list, move_colors, win_map

    # Fallback defaults
    move_list = ['Rock', 'Paper', 'Scissors', 'Fire', 'Sponge', 'Air', 'Water']
    move_colors = {
        'Rock': '#d2691e', 'Paper': '#faf0e6', 'Scissors': '#228b22',
        'Fire': '#ff4500', 'Sponge': '#ffe4c4', 'Air': '#87cefa', 'Water': '#0000cd',
    }
    win_map = {
        'Rock':     ['Fire', 'Scissors', 'Sponge'],
        'Fire':     ['Scissors', 'Sponge', 'Paper'],
        'Scissors': ['Sponge', 'Paper', 'Air'],
        'Sponge':   ['Paper', 'Air', 'Water'],
        'Paper':    ['Air', 'Water', 'Rock'],
        'Air':      ['Water', 'Rock', 'Fire'],
        'Water':    ['Rock', 'Fire', 'Scissors'],
    }
    return move_list, move_colors, win_map


MOVE_LIST, MOVE_COLORS, WIN_MAP = load_from_yaml()


def resolve_round(move_a, move_b):
    """Returns 'a', 'b', or 'draw'."""
    if move_a == move_b:
        return 'draw'
    if move_b in WIN_MAP.get(move_a, []):
        return 'a'
    return 'b'


def generate_code():
    username = app.storage.user.get('username', '').strip()
    if not username:
        ui.notify('Please enter a username first', position='top', type='negative')
        return

    characters = '123456789ABCDEFGHJKMNPQRSTUVWXYZ'
    code = ''.join(random.choices(characters, k=6))
    current_games[code] = {
        'state': 'lobby',      # lobby | picking | reveal | done
        'players': {
            username: {
                'id': app.storage.user['id'],
                'current_move': None,
                'score': 0,
                'last_seen': time.time(),
            }
        },
        'round': 0,
        'last_result': None,   # {'moves': {u: m}, 'winner': username|'draw'}
    }
    ui.navigate.to(f'rps7?game_code={code}')


def join_game(code, username):
    game = current_games.get(code)
    if not game:
        ui.notify('Invalid code', position='top', type='negative')
        return False
    if len(game['players']) >= 2:
        ui.notify('Game is full', position='top', type='negative')
        return False
    if username in game['players']:
        ui.notify('Username already taken', position='top', type='negative')
        return False
    game['players'][username] = {
        'id': app.storage.user['id'],
        'current_move': None,
        'score': 0,
        'last_seen': time.time(),
    }
    if len(game['players']) == 2:
        game['state'] = 'picking'
    return True


def submit_move(code, username, move):
    game = current_games.get(code)
    if not game or game['state'] != 'picking':
        return
    game['players'][username]['current_move'] = move

    # Check if both players have picked
    players = list(game['players'].keys())
    if all(game['players'][p]['current_move'] is not None for p in players):
        # Resolve
        p1, p2 = players
        m1 = game['players'][p1]['current_move']
        m2 = game['players'][p2]['current_move']
        result = resolve_round(m1, m2)
        if result == 'a':
            winner = p1
            game['players'][p1]['score'] += 1
        elif result == 'b':
            winner = p2
            game['players'][p2]['score'] += 1
        else:
            winner = 'draw'

        game['last_result'] = {
            'moves': {p1: m1, p2: m2},
            'winner': winner,
        }
        game['state'] = 'reveal'
        game['round'] += 1


def next_round(code):
    game = current_games.get(code)
    if not game:
        return
    for p in game['players']:
        game['players'][p]['current_move'] = None
    game['last_result'] = None
    game['state'] = 'picking'

def cleanup_stale_players():
    PLAYER_TIMEOUT = 60
    now = time.time()

    games_to_delete = []

    for code, game in current_games.items():
        stale_players = [
            username
            for username, player in game['players'].items()
            if now - player.get('last_seen', 0) > PLAYER_TIMEOUT
        ]

        for username in stale_players:
            del game['players'][username]

        if len(game['players']) == 1:
            game['state'] = 'lobby'

        if not game['players']:
            games_to_delete.append(code)

    for code in games_to_delete:
        del current_games[code]

# ─── Page ──────────────────────────────────────────────────────────────────────

def page(game_code=None):
    # Assign a persistent browser ID
    if 'id' not in app.storage.user:
        app.storage.user['id'] = str(uuid.uuid4())

    # Validate supplied game code
    if game_code and game_code not in current_games:
        ui.notify('Invalid or expired game code', position='top', type='negative')
        game_code = None

    # ── Help dialog (echart from yaml) ─────────────────────────────────────
    with ui.dialog() as help_dialog, ui.card().classes('w-auto'):
        yaml_path = Path(f'{PROJECTS_DIR}/seven.yaml')
        if yaml_path.exists():
            graph_data = yaml.safe_load(yaml_path.read_text())
            ui.echart(graph_data).classes('w-128 h-128')
        else:
            ui.label('Move chart not available').classes('text-lg')
            rows = [{'move': m, 'beats': ', '.join(beats)} for m, beats in WIN_MAP.items()]
            cols = [{'name': 'move', 'label': 'Move', 'field': 'move'},
                    {'name': 'beats', 'label': 'Beats', 'field': 'beats'}]
            ui.table(columns=cols, rows=rows).classes('w-full')

    ui.button(icon='help', on_click=help_dialog.open) \
        .classes('fixed bottom-8 left-8 z-50') \
        .props('size=xl rounded dense')

    # ══════════════════════════════════════════════════════════════════════════
    # LOBBY / JOIN SCREEN  (no game_code yet)
    # ══════════════════════════════════════════════════════════════════════════
    if not game_code:
        with ui.column().classes('w-full items-center gap-6 pt-16'):
            ui.label('Rock Paper Scissors 7').classes('text-5xl font-bold')

            username_input = ui.input('Choose a username') \
                .props('rounded outlined') \
                .classes('w-64')
            username_input.bind_value(app.storage.user, 'username')

            ui.separator().classes('w-64')

            # Join existing game
            with ui.row().classes('gap-2 items-center'):
                code_input = ui.input('Enter game code') \
                    .props('rounded outlined') \
                    .classes('w-48')

                def on_join():
                    uname = app.storage.user.get('username', '').strip()
                    code = code_input.value.strip().upper()
                    if not uname:
                        ui.notify('Enter a username first', type='negative', position='top')
                        return
                    if not code:
                        ui.notify('Enter a game code', type='negative', position='top')
                        return
                    if join_game(code, uname):
                        ui.navigate.to(f'rps7?game_code={code}')

                ui.button('Join', on_click=on_join).props('push color=primary')

            ui.button('Host New Game', on_click=generate_code).props('push color=secondary size=lg')
        return

    # ══════════════════════════════════════════════════════════════════════════
    # IN-GAME SCREEN
    # ══════════════════════════════════════════════════════════════════════════
    username = app.storage.user.get('username', '').strip()
    game = current_games[game_code]

    # If this user isn't in the game yet (e.g. host arrived before join logic)
    # add them — happens when host navigated directly
    if username and username not in game['players']:
        if len(game['players']) < 2:
            game['players'][username] = {
                'id': app.storage.user['id'],
                'current_move': None,
                'score': 0,
                'last_seen': time.time(),
            }
            if len(game['players']) == 2:
                game['state'] = 'picking'

    # ── Username dialog (if unnamed) ───────────────────────────────────────
    with ui.dialog().props('persistent') as username_dialog, ui.card():
        ui.label('Choose a username').classes('text-xl font-bold')
        uname_in = ui.input('Username').props('rounded outlined dense')

        def confirm_username():
            name = uname_in.value.strip()
            if not name:
                ui.notify('Username cannot be empty', type='negative', position='top')
                return
            app.storage.user['username'] = name
            if join_game(game_code, name):
                username_dialog.close()
            # timer will refresh the page state

        ui.button('Join Game', on_click=confirm_username).props('push')

    if not username or username not in game['players']:
        username_dialog.open()

    # ── Main game layout ───────────────────────────────────────────────────
    with ui.column().classes('w-full items-center gap-4 pt-8'):

        ui.label('Rock Paper Scissors 7').classes('text-3xl font-bold')

        # Code display
        with ui.row().classes('items-center gap-2'):
            ui.label(f'Game Code:').classes('text-lg text-gray-500')
            ui.label(game_code).classes('text-2xl font-mono font-bold tracking-widest')
            ui.button(icon='content_copy',
                      on_click=lambda: ui.clipboard.write(game_code)) \
                .props('flat dense round')

        # ── Scoreboard ────────────────────────────────────────────────────
        scoreboard = ui.row().classes('gap-8 items-center')

        # ── Status label ──────────────────────────────────────────────────
        status_label = ui.label('').classes('text-xl text-center')

        # ── Result area ───────────────────────────────────────────────────
        result_card = ui.card().classes('w-full max-w-lg items-center')
        result_card.visible = False

        # ── Move buttons ──────────────────────────────────────────────────
        move_area = ui.column().classes('items-center gap-4')
        with move_area:
            ui.label('Choose your move:').classes('text-lg')
            light_colors = {'#faf0e6', '#ffe4c4', '#87cefa'}
            with ui.row().classes('flex-wrap justify-center gap-3'):
                for move in MOVE_LIST:
                    icon = get_icon(move)
                    color = MOVE_COLORS.get(move, '#888888')
                    text_color = '#000000' if color in light_colors else '#ffffff'
                    ui.button(f'{icon} {move}',
                              on_click=lambda m=move: submit_move(game_code, username, m)) \
                        .classes('text-lg px-4 py-2 font-bold') \
                        .style(f'background-color: {color} !important; color: {text_color} !important;')

        # ── Next round button (hidden until reveal) ────────────────────────
        next_btn = ui.button('▶  Next Round',
                             on_click=lambda: next_round(game_code)) \
            .props('push color=positive size=lg')
        next_btn.visible = False

    # ── Polling timer — refresh UI every 500 ms ────────────────────────────
    def refresh():
        nonlocal username
        username = app.storage.user.get('username', '').strip()
        game = current_games.get(game_code)
        if game and username in game['players']:
            game['players'][username]['last_seen'] = time.time()

        if not game:
            status_label.set_text('Game has ended.')
            move_area.visible = False
            return

        players = list(game['players'].keys())
        state = game['state']

        # Scoreboard
        scoreboard.clear()
        with scoreboard:
            for p in players:
                score = game['players'][p]['score']
                color = 'text-blue-600' if p == username else 'text-red-600'
                with ui.column().classes('items-center'):
                    ui.label(p).classes(f'text-lg font-semibold {color}')
                    ui.label(str(score)).classes('text-3xl font-bold')

        if state == 'lobby':
            status_label.set_text(
                f'Waiting for opponent… share code {game_code}')
            move_area.visible = False
            result_card.visible = False
            next_btn.visible = False

        elif state == 'picking':
            my_move = game['players'].get(username, {}).get('current_move')
            opponents = [p for p in players if p != username]
            opp_moved = opponents and game['players'][opponents[0]]['current_move'] is not None

            if my_move:
                status_label.set_text(
                    f'You picked {get_icon(my_move)} {my_move}. '
                    + ('Waiting for opponent…' if not opp_moved else 'Both picked — resolving…'))
            else:
                status_label.set_text('Your turn — pick a move!')
            move_area.visible = (my_move is None)
            result_card.visible = False
            next_btn.visible = False

        elif state == 'reveal':
            last = game.get('last_result', {})
            moves = last.get('moves', {})
            winner = last.get('winner')

            result_card.clear()
            with result_card:
                ui.label(f'Round {game["round"]} Result').classes('text-xl font-bold')
                with ui.row().classes('gap-8 justify-center mt-2'):
                    for p in players:
                        m = moves.get(p, '?')
                        player_col = 'text-blue-600' if p == username else 'text-red-600'
                        move_color = MOVE_COLORS.get(m, '#888888')
                        with ui.column().classes('items-center'):
                            ui.label(p).classes(f'font-semibold {player_col}')
                            ui.label(get_icon(m)).classes('text-5xl')
                            ui.label(m).classes('text-lg font-bold') \
                                .style(f'color: {move_color};')

                if winner == 'draw':
                    ui.label("It's a draw!").classes('text-2xl font-bold text-yellow-600 mt-2')
                elif winner == username:
                    ui.label('You win! 🎉').classes('text-2xl font-bold text-green-600 mt-2')
                else:
                    ui.label(f'{winner} wins!').classes('text-2xl font-bold text-red-600 mt-2')

            status_label.set_text('')
            result_card.visible = True
            move_area.visible = False
            # Only the host (first player) advances the round to avoid double-trigger
            next_btn.visible = (username == players[0]) if players else False

    ui.timer(0.5, refresh)
    ui.timer(10, cleanup_stale_players)