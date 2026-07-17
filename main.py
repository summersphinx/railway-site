from nicegui import ui
from dotenv import load_dotenv

import os

import home
import about

import background
import menu
import projects


load_dotenv()


STORAGE_SECRET = os.environ['STORAGE_SECRET']

def index():
    background.fractal()

    ui.colors(primary='#580fdf')

    menu.menu()
    menu.footer()

    ui.separator().classes('hidden')

    with ui.column().classes('w-full items-center'):
        ui.sub_pages(
                {
                    '/': home.content,
                    '/about': about.content,
                }
            ).classes('w-full items-center ui-transition')



ui.run(
    index,
    host='0.0.0.0',
    title='XPlus Studios',
    port=8080,
    dark=True,
    favicon="https://gitlab.com/xplus-studios/xplus-toolkit/-/raw/main/logo/Icon-white.ico",
    show=False,
    reload=False,
    storage_secret=STORAGE_SECRET
)