from nicegui import ui

from background import props_content

content_a = '''
A brand new site to show off all of my projects! But only one is currently live, as I am in the middle of moving. More coming soon as I slowly rewrite old projects to work with my new framework


The next project to be implemented will be my project 'CodeRandom'. It was originally designed to be a cryptographic game I made in college, built using PySimpleGUI before they changed to a paid for model. And now that same library is now free to use again. 
'''

def content():
    with ui.card().classes(props_content):
        ui.label(content_a)
