from nicegui import ui, app
from datetime import datetime, timezone
from pathlib import Path



import string
import requests
import random

path = Path(__file__).parent / ""


autokey_words = [
    'AUTO',
    'BARRY',
    'CLAMP',
    'DAIRY',
    'ENGAGE',
    'FAMILY',
    'GRAPE'
]






class Himitsu:

    @staticmethod
    def Flip(word):
        word = list(word)
        word.reverse()
        word = ''.join(word)
        return word

    @staticmethod
    def Shift(word, shift=3, decrypt=False):

        if decrypt:
            shift = -shift

        letters = list(string.ascii_uppercase)

        temp = ''

        word = list(word)

        for letter in word:
            offset = ord(letter) - ord('A')
            wrapped = (offset + shift) % 26
            temp += chr(ord('A') + wrapped)

        return temp

    @staticmethod
    def Autokey(word, key, decrypt=False):

        word = word.upper()
        key = key.upper()

        result = []

        if decrypt:
            # Decryption
            keystream = list(key)
            key_index = 0

            for char in word:
                if char.isalpha():
                    c = ord(char) - ord('A')
                    k = ord(keystream[key_index]) - ord('A')

                    p = (c - k) % 26
                    plain = chr(p + ord('A'))

                    result.append(plain)
                    keystream.append(plain)
                    key_index += 1
                else:
                    result.append(char)

        else:
            # Encryption
            keystream = key + word
            key_index = 0

            for char in word:
                if char.isalpha():
                    p = ord(char) - ord('A')
                    k = ord(keystream[key_index]) - ord('A')

                    c = (p + k) % 26
                    result.append(chr(c + ord('A')))
                    key_index += 1
                else:
                    result.append(char)

        return ''.join(result)


    def __init__(self, word:str|None=None):

        # Get timestamp of today's date
        today_utc = datetime.now(timezone.utc).date()
        midnight_utc = datetime(
            today_utc.year,
            today_utc.month,
            today_utc.day,
            tzinfo=timezone.utc
        )
        unix_timestamp = int(midnight_utc.timestamp())
        r_seed = unix_timestamp * int(today_utc.day) + today_utc.year
        r_seed = round(r_seed / today_utc.month)
        random.seed(r_seed) # Set a new random daily seed.

        # Get phrase List
        url = 'https://gitlab.com/xplus-studios/xplus.dev-images/-/raw/main/projects/cr5-phrases.txt'
        req = requests.get(url).text

        words = req.split('\n') # Set a list from the wordlist


        self.word = word # If word gets manually set

        if self.word is None:
            self.word = random.choice(words) # Grab random phrase

        self.actual = self.word # Save a copy of unedited word.


        # Modify word str to work with encryption.
        self.word = self.word.upper()
        self.word = self.word.replace(' ','')
        self.word = self.word.split('—')[0]
        self.word = ''.join(ch for ch in self.word if ch not in string.punctuation)
        self.encryption = self.word

        self.sequence = random.randint(3, 5) # Random number of encryption steps


        # Define encryption methods
        self.methods = [
            'Flip',
            'Shift',
            'Autokey',
        ]

        self.steps = []
        old_new = ''

        for each in range(self.sequence):
            while True:
                new = random.choice(self.methods)
                if new != old_new:
                    old_new = new
                    break

            if new == 'Autokey':
                new_key = random.choice(autokey_words)
                self.encryption = Himitsu.Autokey(self.encryption, new_key)
                self.steps.append( {
                    'step': 'Autokey',
                    'key': new_key,
                    'word': self.encryption,
                })

            elif new == 'Shift':
                new_key = random.randint(3, 24)
                self.encryption = Himitsu.Shift(self.encryption, new_key)
                self.steps.append( {
                    'step': 'Shift',
                    'key': new_key,
                    'word': self.encryption,
                })
            elif new == 'Flip':
                self.encryption = Himitsu.Flip(self.encryption)
                self.steps.append( {
                    'step': 'Flip',
                    'word': self.encryption,
                })
            else:
                print(f'ERROR: INVALID STEP: {new}. PLEASE FIX')

        print(self.steps)


# Cards for Steps

# Card Styling
styling_subtitle = 'absolute bottom-2 right-2 text-right sm:w-3/5 text-emerald-600'

def build_Blank(container):
    with container:
        ui.label('-').classes(styling_subtitle)

    return {'step': '-'}


def build_Flip(container):
    with container:
        ui.label('Replaces each letter with its opposite in the alphabet.').classes(styling_subtitle)

    return {'step': 'Flip'}


def build_Shift(container):
    w = {'step': 'Shift', 'value': 3}
    with container:
        ui.label('Shifts each letter in the alphabet by a fixed number of positions.').classes(styling_subtitle)
        ui.label()
        ui.slider(min=1, max=25, step=1, value=3) \
        .props('markers snap label-always switch-label-side color=pink-14 track-size=8px') \
        .classes('w-7/8 self-center') \
        .bind_value_to(w, 'value')

    return w


def build_Autokey(container):
    w = {'step': 'Autokey', 'value': ''}
    with container:
        ui.label('Uses a keyword followed by the plaintext itself to determine how each letter is encrypted.').classes(styling_subtitle)
        ui.label()
        ui.select(autokey_words, value='AUTO').props('outlined dense').classes('w-36 px-4') \
        .bind_value_to(w, 'value')

    return w


BUILDERS = {
    '-': build_Blank,
    'Atbash': build_Flip,
    'Caesar': build_Shift,
    'Autokey': build_Autokey,
}


def page():

    word = Himitsu()

    app.add_static_files('/static', Path(f'{path}/static'))

    ui.add_head_html('''
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400;1,700&display=swap" rel="stylesheet">

    <style>
    body {
        font-family: 'Space Mono', monospace;
    }
    </style>
    ''')

    ui.colors(primary='#f7aef8')

    state = {'step_count': 0}

    with ui.dialog() as dialog, ui.card():
        ui.label("Rules").classes('text-2xl text-bold')
        ui.separator()
        ui.label("Decrypt the phrase in 3-5 steps.")
        h_icons = [
            ['light-green-13', 'The step and data is correct.'],
            ['pink-12', 'The step is in the right spot, but missing the right data.'],
            ['yellow-13', 'The step is is the wrong spot and missing the right data.'],
            ['blue-13', 'The step is in the wrong spot, but has the right data.'],
            ['grey-9', 'Then step doesn\'t exist, or hasn\'t been tried.']
        ]

        for each in h_icons:
            with ui.list().classes(''):
                with ui.item():
                    with ui.item_section().props('avatar'):
                        ui.icon('token').props(f'color={each[0]}')
                    with ui.item_section().props():
                        ui.label(each[1])

        dialog.open()


    ui.button(icon='help', on_click=dialog.open).props('rounded color=deep-purple-8 padding=2px') \
    .classes('fixed p-0 m-0 text-2xl')


    with ui.card().classes('md:w-3/4 w-full self-center'):
        ui.label(word.encryption).classes('tracking-widest text-bold self-center')

        def decrypt(e):
            d = word.encryption
            reversed_steps = list(reversed(word.steps))

            def signature(step_dict):
                if step_dict['step'] == 'Flip':
                    return (step_dict['step'], None)
                return (step_dict['step'], step_dict.get('key'))

            for idx, each in enumerate(steps_data):
                w = each['widgets']
                indicator = each['indicator']

                actual = reversed_steps[idx] if idx < len(reversed_steps) else None

                if actual is None or w['step'] == '-':
                    # No guess made (or no corresponding real step here)
                    color = 'grey-6'
                else:
                    guess_sig = (w['step'], None if w['step'] == 'Flip' else w.get('value'))
                    own_sig = signature(actual)

                    other_sigs = [signature(s) for j, s in enumerate(reversed_steps) if j != idx]

                    if guess_sig == own_sig:
                        # Right method, right data, right spot
                        color = 'teal-14'
                    elif guess_sig in other_sigs:
                        # Right method + data, but it belongs to a different position
                        color = 'blue-9'
                    elif w['step'] == actual['step']:
                        # Right spot, right method, wrong data
                        color = 'pink-4'
                    else:
                        # Wrong method entirely for this spot
                        color = 'amber-9'

                indicator.props(f'color={color}')

                if w['step'] == 'Shift':
                    d = Himitsu.Shift(d, w['value'], decrypt=True)
                elif w['step'] == 'Flip':
                    d = Himitsu.Flip(d)
                elif w['step'] == 'Autokey':
                    d = Himitsu.Autokey(d, key=w['value'], decrypt=True)

            e.set_value(d)

        with ui.row().classes('w-full'):

            output = ui.input("Decrypted").props('outlined dense readonly').classes('grow')
            ui.button('Submit', on_click=lambda e=output: decrypt(e)).props('outline')

    with ui.card().classes('md:w-3/4 w-full self-center'):

        with ui.row():

            def add_step():

                if state['step_count'] >= 5:
                    return

                step_data = {'widgets': {}, 'indicator': None}

                with steps_list:
                    with ui.card().tight().classes('w-full relative'):
                        def on_change(e):
                            rebuild(e.value)

                        with ui.row().classes('w-full'):

                            ui.select(['-', 'Atbash', 'Caesar', 'Autokey'], value='-',
                                      on_change=on_change) \
                                .props('standout dense').classes('w-32')

                            ui.space().classes('grow')

                            indicator = ui.icon('token').props('color=grey-6').classes('text-2xl self-center mr-8')
                            step_data['indicator'] = indicator

                        ui.separator()

                        body = ui.column().classes('w-full h-36 py-0 my-0')  # dynamic content lives here

                        def rebuild(step_type):
                            body.clear()
                            builder = BUILDERS.get(step_type, build_Blank)
                            step_data['widgets'] = builder(body)
                            indicator.props('color=grey-6')  # reset indicator color on step-type change

                        rebuild('-')  # initial render

                steps_data.append(step_data)
                state['step_count'] = len(steps_data)

            def remove_step():
                if state['step_count'] <= 3:
                    return
                steps_list.remove(state['step_count']-1)
                steps_data.pop(-1)
                state['step_count'] = len(steps_data)


            ui.label('Encryption Steps:').classes('text-bold sm:text-lg text-md pl-4 self-center')

            with ui.card().tight().props(''):

                with ui.row():
                    ui.button('-', on_click=remove_step).props('color=pink-14').classes('text-bold p-1 mx-0')
                    ui.label('3').classes('text-bold sm:text-lg text-md self-center -m-2') \
                    .bind_text_from(state, 'step_count', backward=lambda n: str(n))
                    ui.button('+', on_click=add_step).props('color=teal-14').classes('text-bold p-1 mx-0')

        ui.separator()

        steps_list = ui.column().classes('w-full')
        steps_data = []  # one dict per step, holding its live widgets

        for i in range(3):
            add_step()