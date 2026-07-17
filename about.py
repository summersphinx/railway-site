from nicegui import ui

from background import props_content
from background import md_css

md_text = '''
# THIS JUST IN!!!

A solo dev team from Montana, USA. I enjoy tinkering with random projects and building random stuff. Currently
working through getting certified for Pen Testing and Cyber Security Analyst. I started my coding adventures 
in high school learning JS. After 2 years, I switched to Python, and have built most of my projects with it since.

I don't have much time to work on new projects at the moment, but I try to at least get 4-5 hours in a week to
work on a new or old project.
'''


def content():
    ui.add_css(md_css)
    with ui.card().classes(props_content):
        ui.markdown(md_text)