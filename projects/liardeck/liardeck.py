from nicegui import ui, app
from PIL import Image

import random as rand

deck = [
    'A'*6,
    'Q'*6,
    'K'*6,
    'J'*2
]

temp_cards = [
    Image.new("RGB", (1000, 1554), "blue"),
    Image.new("RGB", (1000, 1554), "blue"),
    Image.new("RGB", (1000, 1554), "blue"),
    Image.new("RGB", (1000, 1554), "orange"),
    Image.new("RGB", (1000, 1554), "orange"),
    Image.new("RGB", (1000, 1554), "orange"),
    Image.new("RGB", (1000, 1554), "green"),
    Image.new("RGB", (1000, 1554), "green"),
    Image.new("RGB", (1000, 1554), "green"),
    Image.new("RGB", (1000, 1554), "purple"),
]
temp_cards += temp_cards

selected_indices = set()


class Game:
    def __init__(self):
        pass

class Deck:
    def __init__(self):
        pass



def toggle_card(index: int, card: ui.image):
    if index in selected_indices:
        selected_indices.remove(index)
        card.classes(remove='selected')
    elif len(selected_indices) + 1 <= 3:
        selected_indices.add(index)
        card.classes(add='selected')
    else:
        ui.notify('Max playable cards reached!', position='top', type='warning')
    status.text = f'Selected: {sorted(selected_indices)}'

def page():
    ui.add_head_html('''
    <style type="text/tailwindcss">
        @layer components {
            .card {
                @apply w-64 -mx-16 rounded-xl border-4 border-white transition hover:-translate-y-10;
            }
            
            .unselected {
            
            }
            
            .selected {
                @apply -my-8 invert-100 transition hover:-translate-y-5;
            }
        }
    </style>
    ''')
    hand = rand.choices(list(enumerate(temp_cards)), k=6)  # keep (original_index, img) pairs if you need identity

    with ui.card().classes('absolute overflow-hidden bottom-0 self-center w-4/5'):
        with ui.row().classes('relative self-center -bottom-8'):
            for i, (orig_idx, img) in enumerate(hand):
                card = ui.image(img).classes(
                    'unselected card '
                )
                card.on('click', lambda e, idx=i, c=card: toggle_card(idx, c))

    global status
    status = ui.label('Selected: []').classes('mt-4 text-sm text-gray-600')