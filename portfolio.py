from nicegui import ui


page_css = '''
'''

page_md = '''
# Gavin Wood

summersphinx@duck.com

## Projects


'''

def content():
    ui.add_css(page_css)
    ui.markdown(page_md)