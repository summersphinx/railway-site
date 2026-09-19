from nicegui import ui, app

import background
import menu

import traceback
import importlib.util
import sys
from pathlib import Path
import yaml

PROJECTS_DIR = Path(__file__).parent / "projects"

image_fade = '''
    mask-image: linear-gradient(to right, black 50%, transparent 90%);
    -webkit-mask-image: linear-gradient(to right, black 50%, transparent 90%);
'''

def load_projects():
    for header_path in sorted(PROJECTS_DIR.glob("*/header.yaml")):
        project_dir = header_path.parent
        project_name = project_dir.name

        with open(header_path) as f:
            meta = yaml.safe_load(f)

        entry = meta.get("entry")
        route = meta.get("route")

        if not entry:
            print(f"[projects] Skipping {project_name}: no entry in header.yaml")
            continue
        if not route:
            print(f"[projects] Skipping {project_name}: no route in header.yaml")
            continue

        entry_path = project_dir / entry
        if not entry_path.exists():
            print(f"[projects] Skipping {project_name}: {entry} not found")
            continue

        if str(project_dir) not in sys.path:
            sys.path.insert(0, str(project_dir))

        module_name = f"projects.{project_name}.{entry_path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, entry_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        if not hasattr(module, 'page'):
            print(f"[projects] Skipping {project_name}: no page() function in {entry}")
            continue

        # Register the route using the url from header.yaml
        ui.page(route)(module.page)
        print(f"[projects] Registered: {route} → {entry}")

load_projects()

# Route non-existent projects to /projects
@ui.page('/projects/{p}')
def not_found(p):
    ui.navigate.to('/projects')

@ui.page('/projects')
def main():
    background.fractal()
    menu.menu()
    menu.footer()

    with ui.column().classes('w-full items-center props-content'):
        with ui.card().classes(background.props_content):
            ui.label('Projects').classes('text-xl text-bold')

            with ui.column().classes('gap-4 w-full items-center'):
                for header_path in sorted(PROJECTS_DIR.glob("*/header.yaml")):
                    project_dir = header_path.parent
                    project_name = project_dir.name

                    with open(header_path) as f:
                        meta = yaml.safe_load(f)

                    entry = meta.get("entry")
                    route = meta.get("route")

                    if not entry:
                        print(f"[projects] Skipping {project_name}: no entry in header.yaml")
                        continue
                    if not route:
                        print(f"[projects] Skipping {project_name}: no route in header.yaml")
                        continue

                    entry_path = project_dir / entry
                    if not entry_path.exists():
                        print(f"[projects] Skipping {project_name}: {entry} not found")
                        continue

                    with ui.card().props('').classes('w-full mb-4 max-w-5xl h-64 transition duration-300 ease-in-out hover:scale-110').on('click', lambda r=route: ui.navigate.to(r)).classes('cursor-pointer'):

                        with ui.row().classes('w-full'):
                            ui.image(meta.get('image')).classes('w-1/3 h-50 object-scale-down')
                            with ui.column().classes(''):
                                ui.label(meta.get('title')).classes('md:absolute md:top-2 md:right-2 text-right md:text-4xl sm:text-xl font-bold text-violet-400')
                                ui.label(meta.get('description')).classes('md:absolute md:bottom-1 md:right-1 sm:invisible md:visible text-right text-lg')
