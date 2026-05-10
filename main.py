from nicegui import ui


CANVAS_HTML = '''
<canvas id="fractal-canvas" style="
    position:fixed;inset:0;z-index:0;
    width:100vw;height:100vh;
    background:#050510;
"></canvas>
<div id="fractal-label" style="
    position:fixed;bottom:2rem;left:75%;transform:translateX(-50%);
    z-index:100;font-family:monospace;font-size:11px;
    letter-spacing:.3em;text-transform:uppercase;
    color:rgba(255,255,255,.35);transition:opacity .6s;
    pointer-events:none;
"></div>
<script>
document.addEventListener('DOMContentLoaded', function () {

    var canvas = document.getElementById('fractal-canvas');
    var ctx    = canvas.getContext('2d');

    function resize() {
        canvas.width  = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', function () { resize(); nextFractal(); });

    var PALETTES = [
        ['#b702db', '#dbb702', '#02dbb7'],
        ['#1be7a0', '#e71bc8', '#e73a1b'],
        ['#00ffe7','#00c9ff','#7b2fff'],
        ['#ffe066','#ff6f3c','#ff2d78'],
        ['#a8ff78','#48ff9a','#00b4d8'],
        ['#ff61d2','#fe9090','#7b61ff'],
        ['#ff9f1c', '#ff4040', '#7b2cbf'],
        ['#2ec4b6', '#cbf3f0', '#ffbf69'],
        ['#f72585', '#7209b7', '#3a0ca3'],
        ['#4cc9f0', '#4895ef', '#4361ee'],
        ['#80ffdb', '#64dfdf', '#5390d9'],
        ['#ffd60a', '#ff006e', '#8338ec'],
        ['#06d6a0', '#118ab2', '#073b4c'],
        ['#f15bb5', '#fee440', '#00bbf9'],
        ['#caffbf', '#9bf6ff', '#bdb2ff'],
        ['#ffadad', '#ffd6a5', '#fdffb6']
    ];
    var NAMES = [
        'Sierpinski Triangle',
        'Koch Snowflake',
        'Fractal Tree',
        'Dragon Curve',
        'Barnsley Fern',
        'Pythagoras Tree',
        'Levy C Curve',
        'Recursive Circles',
        'Fractal Lightning'
    ];

    var fractalIdx = 0, rafId, fadeRaf, tasks = [], qi = 0, startT = 0;

    function setLabel(name) {
        var el = document.getElementById('fractal-label');
        if (!el) return;
        el.style.opacity = '0';
        setTimeout(function () { el.textContent = name; el.style.opacity = '1'; }, 400);
    }

    /* ── Sierpinski ─────────────────────────────────────────── */
    function buildSierpinski(pal) {
        var t = [], W = canvas.width, H = canvas.height;
        var sz = Math.min(W, H) * 0.78;
        var cx = W / 2, ty = (H - sz * 0.866) / 2;
        function tri(x1,y1,x2,y2,x3,y3,d) {
            if (d === 0) {
                (function (a,b,c,e,f,g) {
                    t.push(function () {
                        ctx.beginPath();
                        ctx.moveTo(a,b); ctx.lineTo(c,e); ctx.lineTo(f,g);
                        ctx.closePath();
                        var gr = ctx.createLinearGradient(a,b,f,g);
                        gr.addColorStop(0,pal[0]); gr.addColorStop(.5,pal[1]); gr.addColorStop(1,pal[2]);
                        ctx.fillStyle = gr; ctx.fill();
                    });
                })(x1,y1,x2,y2,x3,y3);
                return;
            }
            var mx12=(x1+x2)/2,my12=(y1+y2)/2,mx23=(x2+x3)/2,my23=(y2+y3)/2,mx13=(x1+x3)/2,my13=(y1+y3)/2;
            tri(x1,y1,mx12,my12,mx13,my13,d-1);
            tri(mx12,my12,x2,y2,mx23,my23,d-1);
            tri(mx13,my13,mx23,my23,x3,y3,d-1);
        }
        tri(cx,ty, cx-sz/2,ty+sz*.866, cx+sz/2,ty+sz*.866, 6);
        return t;
    }

    /* ── Koch Snowflake ─────────────────────────────────────── */
    function buildKoch(pal) {
        var t = [], W = canvas.width, H = canvas.height;
        var R = Math.min(W,H) * 0.34, cx = W/2, cy = H/2;
        function seg(ax,ay,bx,by,d) {
            if (d === 0) {
                (function (a,b,c,e,col) {
                    t.push(function () {
                        ctx.beginPath(); ctx.moveTo(a,b); ctx.lineTo(c,e);
                        ctx.strokeStyle = col; ctx.lineWidth = 1.5; ctx.stroke();
                    });
                })(ax,ay,bx,by, pal[t.length % 3]);
                return;
            }
            var dx=bx-ax,dy=by-ay;
            var p1x=ax+dx/3,p1y=ay+dy/3,p2x=ax+2*dx/3,p2y=ay+2*dy/3;
            var a=Math.atan2(dy,dx)-Math.PI/3, l=Math.sqrt(dx*dx+dy*dy)/3;
            var pkx=p1x+Math.cos(a)*l, pky=p1y+Math.sin(a)*l;
            seg(ax,ay,p1x,p1y,d-1); seg(p1x,p1y,pkx,pky,d-1);
            seg(pkx,pky,p2x,p2y,d-1); seg(p2x,p2y,bx,by,d-1);
        }
        for (var i=0;i<3;i++) {
            var a=Math.PI/2+i*2*Math.PI/3, b=a+2*Math.PI/3;
            seg(cx+R*Math.cos(a),cy+R*Math.sin(a), cx+R*Math.cos(b),cy+R*Math.sin(b), 5);
        }
        return t;
    }

    /* ── Fractal Tree ───────────────────────────────────────── */
    function buildTree(pal) {
        var t = [], W = canvas.width, H = canvas.height;
        var sx=W/2, sy=H*0.92, tl=H*0.17;
        function br(x,y,a,l,d) {
            if (l < 3) return;
            var ex=x+Math.cos(a)*l, ey=y+Math.sin(a)*l;
            var col=d>3?pal[0]:d>1?pal[1]:pal[2], lw=Math.max(1,l*0.07);
            (function (x1,y1,x2,y2,c,w) {
                t.push(function () {
                    ctx.beginPath(); ctx.moveTo(x1,y1); ctx.lineTo(x2,y2);
                    ctx.strokeStyle=c; ctx.lineWidth=w; ctx.lineCap='round'; ctx.stroke();
                });
            })(x,y,ex,ey,col,lw);
            br(ex,ey,a-0.4,l*0.68,d-1);
            br(ex,ey,a+0.37,l*0.64,d-1);
        }
        br(sx,sy,-Math.PI/2,tl,10);
        return t;
    }

    /* ── Dragon Curve ───────────────────────────────────────── */
    function buildDragon(pal) {
        var t = [], W = canvas.width, H = canvas.height;
        // Paper-folding sequence: fold n times, read folds L/R (1=right, -1=left)
        var seq = [1];
        for (var i=1;i<14;i++) {
            var rev=[];
            for (var j=seq.length-1;j>=0;j--) { rev.push(-seq[j]); }
            seq = seq.concat([1]).concat(rev);
        }
        var sp=Math.min(W,H)*0.011, x=W*0.47, y=H*0.52, dir=0;
        var DX=[1,0,-1,0], DY=[0,-1,0,1];
        for (var k=0;k<seq.length;k++) {
            (function (x1,y1,x2,y2,col) {
                t.push(function () {
                    ctx.beginPath(); ctx.moveTo(x1,y1); ctx.lineTo(x2,y2);
                    ctx.strokeStyle=col; ctx.lineWidth=1.5; ctx.stroke();
                });
            })(x,y, x+DX[dir]*sp, y+DY[dir]*sp, pal[k%3]);
            x+=DX[dir]*sp; y+=DY[dir]*sp;
            dir=(dir+(seq[k]>0?3:1)+4)%4;
        }
        return t;
    }

    /* ── Barnsley Fern ──────────────────────────────────────── */
    function buildFern(pal) {
        var t = [], W = canvas.width, H = canvas.height;
        var x = 0, y = 0;
        var scale = Math.min(W, H) * 0.085;
        var ox = W / 2, oy = H * 0.92;

        for (var i = 0; i < 18000; i++) {
            var nx, ny, r = Math.random();

            if (r < 0.01) {
                nx = 0;
                ny = 0.16 * y;
            } else if (r < 0.86) {
                nx = 0.85 * x + 0.04 * y;
                ny = -0.04 * x + 0.85 * y + 1.6;
            } else if (r < 0.93) {
                nx = 0.2 * x - 0.26 * y;
                ny = 0.23 * x + 0.22 * y + 1.6;
            } else {
                nx = -0.15 * x + 0.28 * y;
                ny = 0.26 * x + 0.24 * y + 0.44;
            }

            x = nx;
            y = ny;

            if (i > 20) {
                (function (px, py, col) {
                    t.push(function () {
                        ctx.fillStyle = col;
                        ctx.globalAlpha = 0.78;
                        ctx.fillRect(px, py, 1.4, 1.4);
                        ctx.globalAlpha = 1;
                    });
                })(ox + x * scale, oy - y * scale, pal[i % 3]);
            }
        }
        return t;
    }

    /* ── Pythagoras Tree ────────────────────────────────────── */
    function buildPythagoras(pal) {
        var t = [], W = canvas.width, H = canvas.height;
        var base = Math.min(W, H) * 0.13;
        var cx = W / 2, y = H * 0.86;

        function square(x, y, size, angle, depth) {
            if (depth <= 0 || size < 3) return;

            var c = Math.cos(angle), s = Math.sin(angle);
            var x1 = x, y1 = y;
            var x2 = x + c * size, y2 = y + s * size;
            var x3 = x2 + s * size, y3 = y2 - c * size;
            var x4 = x + s * size, y4 = y - c * size;

            (function (a,b,cx2,cy2,d,e,f,g,col,alpha) {
                t.push(function () {
                    ctx.beginPath();
                    ctx.moveTo(a,b);
                    ctx.lineTo(cx2,cy2);
                    ctx.lineTo(d,e);
                    ctx.lineTo(f,g);
                    ctx.closePath();
                    ctx.fillStyle = col;
                    ctx.globalAlpha = alpha;
                    ctx.fill();
                    ctx.globalAlpha = 1;
                });
            })(x1,y1,x2,y2,x3,y3,x4,y4,pal[depth % 3],0.82);

            var next = size * 0.707;
            square(x4, y4, next, angle - Math.PI / 4, depth - 1);
            square(x3 - Math.cos(angle + Math.PI / 4) * next, y3 - Math.sin(angle + Math.PI / 4) * next, next, angle + Math.PI / 4, depth - 1);
        }

        square(cx - base / 2, y, base, 0, 9);
        return t;
    }

    /* ── Levy C Curve ───────────────────────────────────────── */
    function buildLevy(pal) {
        var t = [], W = canvas.width, H = canvas.height;
        var size = Math.min(W, H) * 0.52;
        var ax = W / 2 - size / 2, ay = H / 2 + size * 0.12;
        var bx = W / 2 + size / 2, by = H / 2 + size * 0.12;

        function levy(x1, y1, x2, y2, depth) {
            if (depth === 0) {
                (function (a,b,c,d,col) {
                    t.push(function () {
                        ctx.beginPath();
                        ctx.moveTo(a,b);
                        ctx.lineTo(c,d);
                        ctx.strokeStyle = col;
                        ctx.lineWidth = 1.25;
                        ctx.stroke();
                    });
                })(x1,y1,x2,y2,pal[t.length % 3]);
                return;
            }

            var mx = (x1 + x2) / 2 + (y1 - y2) / 2;
            var my = (y1 + y2) / 2 + (x2 - x1) / 2;
            levy(x1, y1, mx, my, depth - 1);
            levy(mx, my, x2, y2, depth - 1);
        }

        levy(ax, ay, bx, by, 14);
        return t;
    }

    /* ── Recursive Circles ──────────────────────────────────── */
    function buildCircles(pal) {
        var t = [], W = canvas.width, H = canvas.height;
        var cx = W / 2, cy = H / 2;
        var start = Math.min(W, H) * 0.27;

        function circles(x, y, r, depth) {
            if (depth <= 0 || r < 4) return;

            (function (px, py, pr, col, lw) {
                t.push(function () {
                    ctx.beginPath();
                    ctx.arc(px, py, pr, 0, Math.PI * 2);
                    ctx.strokeStyle = col;
                    ctx.lineWidth = lw;
                    ctx.globalAlpha = 0.86;
                    ctx.stroke();
                    ctx.globalAlpha = 1;
                });
            })(x, y, r, pal[depth % 3], Math.max(1, r * 0.012));

            var nr = r * 0.48;
            for (var i = 0; i < 6; i++) {
                var a = i * Math.PI / 3 + depth * 0.14;
                circles(x + Math.cos(a) * r * 0.72, y + Math.sin(a) * r * 0.72, nr, depth - 1);
            }
        }

        circles(cx, cy, start, 5);
        return t;
    }

    /* ── Fractal Lightning ───────────────────────────────────── */
    function buildLightning(pal) {
        var t = [], W = canvas.width, H = canvas.height;
        var startX = W * (0.35 + Math.random() * 0.3);
        var startY = H * 0.04;
        var endX = W * (0.25 + Math.random() * 0.5);
        var endY = H * 0.86;

        function bolt(x1, y1, x2, y2, depth, energy) {
            if (depth <= 0) {
                var col = pal[Math.floor(Math.random() * pal.length)];
                var width = Math.max(0.7, energy * 2.8);

                (function (a, b, c, d, glow, w, alpha) {
                    t.push(function () {
                        ctx.save();

                        ctx.shadowBlur = 22 * alpha;
                        ctx.shadowColor = glow;
                        ctx.strokeStyle = 'rgba(255,255,255,' + Math.min(0.95, alpha + 0.22) + ')';
                        ctx.lineWidth = w * 0.42;
                        ctx.lineCap = 'round';

                        ctx.beginPath();
                        ctx.moveTo(a, b);
                        ctx.lineTo(c, d);
                        ctx.stroke();

                        ctx.strokeStyle = glow;
                        ctx.globalAlpha = alpha;
                        ctx.lineWidth = w;
                        ctx.beginPath();
                        ctx.moveTo(a, b);
                        ctx.lineTo(c, d);
                        ctx.stroke();

                        ctx.restore();
                    });
                })(x1, y1, x2, y2, col, width, Math.max(0.28, energy));

                return;
            }

            var dx = x2 - x1;
            var dy = y2 - y1;
            var len = Math.sqrt(dx * dx + dy * dy);
            var midX = (x1 + x2) / 2;
            var midY = (y1 + y2) / 2;
            var normalX = -dy / len;
            var normalY = dx / len;
            var jag = len * (0.16 + Math.random() * 0.24) * depth / 8;

            midX += normalX * (Math.random() * 2 - 1) * jag;
            midY += normalY * (Math.random() * 2 - 1) * jag;

            bolt(x1, y1, midX, midY, depth - 1, energy);
            bolt(midX, midY, x2, y2, depth - 1, energy * 0.96);

            if (Math.random() < 0.52 && depth < 7) {
                var angle = Math.atan2(dy, dx) + (Math.random() < 0.5 ? -1 : 1) * (0.45 + Math.random() * 0.72);
                var branchLen = len * (0.24 + Math.random() * 0.34);
                var bx = midX + Math.cos(angle) * branchLen;
                var by = midY + Math.sin(angle) * branchLen;
                bolt(midX, midY, bx, by, depth - 2, energy * 0.54);
            }
        }

        for (var flash = 0; flash < 3; flash++) {
            var offset = (flash - 1) * Math.min(W, H) * 0.012;
            bolt(startX + offset, startY, endX - offset, endY, 8, 1);
        }

        return t;
    }

    var BUILDERS = [
        buildSierpinski,
        buildKoch,
        buildTree,
        buildDragon,
        buildFern,
        buildPythagoras,
        buildLevy,
        buildCircles,
        buildLightning
    ];

    /* ── Fade → next ────────────────────────────────────────── */
    function fadeThenNext() {
        var alpha = 1;
        function step() {
            ctx.globalAlpha = 0.1;
            ctx.fillStyle = '#050510';
            ctx.fillRect(0,0,canvas.width,canvas.height);
            ctx.globalAlpha = 1;
            alpha -= 0.02;
            if (alpha > 0) { fadeRaf = requestAnimationFrame(step); }
            else { ctx.clearRect(0,0,canvas.width,canvas.height); nextFractal(); }
        }
        fadeRaf = requestAnimationFrame(step);
    }

    /* ── Driver ─────────────────────────────────────────────── */
        function nextFractal() {
            cancelAnimationFrame(rafId);
            cancelAnimationFrame(fadeRaf);
            ctx.clearRect(0,0,canvas.width,canvas.height);
            ctx.globalAlpha = 1;

            var pal = PALETTES[Math.floor(Math.random() * PALETTES.length)];
            setLabel(NAMES[fractalIdx]);
            var rawTasks = BUILDERS[fractalIdx](pal);
            fractalIdx = Math.floor(Math.random() * BUILDERS.length);

            var totalMs = rawTasks.length < 500 ? 2000 : rawTasks.length < 5000 ? 2500 : 3200;
            var step = totalMs / rawTasks.length;
            tasks = rawTasks.map(function (fn, i) { return { fn: fn, delay: i * step }; });
        qi = 0; startT = 0;

        function draw(ts) {
            if (!startT) startT = ts;
            var el = ts - startT;
            while (qi < tasks.length && tasks[qi].delay <= el) { tasks[qi].fn(); qi++; }
            if (qi < tasks.length) { rafId = requestAnimationFrame(draw); }
            else { setTimeout(fadeThenNext, 3000); }
        }
        rafId = requestAnimationFrame(draw);
    }

    window.nextFractal = nextFractal;
    nextFractal();
});
</script>
'''


@ui.page('/')
def index():

    ui.add_head_html('<script src="https://kit.fontawesome.com/ac723d76fa.js" crossorigin="anonymous"></script>')
    ui.add_head_html('''
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@300;600&family=Share+Tech+Mono&display=swap');
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #050510; overflow-y: auto; overflow-x:hidden; font-family: 'Rajdhani', sans-serif; }
        #app  { position: relative; z-index: 5; }

        #vignette {
            position: fixed; inset: 0; z-index: 1; pointer-events: none;
            background: radial-gradient(ellipse at center, transparent 40%, rgba(5,5,16,.72) 100%);
        }
        .layout-center {
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            min-height: 100vh; padding: 2rem;
        }
        .glass-card-content {
            background: rgba(255,255,255,.045);
            border: 1px solid rgba(255,255,255,.12);
            backdrop-filter: blur(3px) saturate(160%);
            -webkit-backdrop-filter: blur(18px) saturate(160%);
            border-radius: 1.4rem; padding: 2.8rem 3.2rem;
            margin-top: 4.0rem; width: 75%; text-align: center;
            box-shadow: 0 8px 40px rgba(0,0,0,.55), inset 0 1px 0 rgba(255,255,255,.1);
        }
        .glass-card-bar {
            background: rgba(255,255,255,.045);
            border: 1px solid rgba(255,255,255,.12);
            backdrop-filter: blur(18px) saturate(160%);
            -webkit-backdrop-filter: blur(18px) saturate(160%);
            border-radius: 1.0rem; padding: 0.8rem 3.2rem;
            margin-top: 10px;width: 80%; text-align: center;
            box-shadow: 0 8px 40px rgba(0,0,0,.55), inset 0 1px 0 rgba(255,255,255,.1);
        }

        .ui-transition {
            transition: opacity 0.35s ease, transform 0.35s ease;
        }
        .ui-transition.ui-hidden {
            opacity: 0;
            pointer-events: none;
            transform: translateY(-10px);
        }
    </style>
    ''')

    # Canvas goes into body_html — placed before #app in the template,
    # so it exists in the DOM before Vue mounts.
    ui.add_body_html(CANVAS_HTML)

    ui.html('<div id="vignette"></div>')

    ui.colors(primary='#580fdf')

    def toggle_ui(e):
        visible = e.value
        ui.run_javascript(f'''
            document.querySelectorAll(".ui-transition").forEach(function(el) {{
                el.classList.toggle("ui-hidden", {str(not visible).lower()});
            }});
        ''')

    hide_ui = ui.checkbox(value=True, on_change=toggle_ui).props('color=info size=100px checked-icon=visibility_off unchecked-icon=visibility dense').classes('fixed top-8 right-8 z-210')
    with hide_ui:
        ui.tooltip('Hide UI').classes('text-lg')

    with ui.header().classes('glass-card-bar justify-self-center ui-transition'):
        with ui.button(on_click=lambda: ui.notify('Home')).classes('grow h-full').props('flat'):
            ui.image('https://gitlab.com/summersphinx/xplus-games-toolkit/-/raw/main/logo/xplus2.png').props('fit=scale-down').classes('h-16')
        header_links = {
            'Projects': lambda: ui.notify('Projects'),
            'About': lambda: ui.notify('About'),
            'Contact': lambda: ui.notify('Contact'),
        }
        for t, a in header_links.items():
            ui.button(t, on_click=a).classes('grow h-full text-2xl text-bold').props('flat')

        header_ext_links = {
            'Gitlab': ['fa-brands fa-gitlab', 'https://gitlab.com/summersphinx/'],
            'Discord': ['fa-brands fa-discord', 'https://discord.gg/kXdbByHCre'],
            'Itch': ['fa-brands fa-itch-io', 'https://itch.io']
        }
        with ui.row().classes('grow'):
            for t, d in header_ext_links.items():
                with ui.button(on_click=lambda url=d[1]: ui.navigate.to(url, new_tab=True)).classes('grow items-center justify-center').props('flat rounded'):
                    ui.icon(d[0]).classes('text-4xl text-center')
                    ui.tooltip(t).classes('text-lg')


    with ui.footer(fixed=False).classes('bg-transparent w-full h-16 items-center'):
        footer_content = [
            ["Created with ", "NiceGUI", "https://nicegui.io"],
            ["Hosted on ", "Railway.app", "https://railway.com?referralCode=CN9B5I"],
        ]
        with ui.grid(columns=1).classes('w-full items-center justify-center text-center'):
            ui.label('© 2026 X+ Studios. All rights reserved.').classes('text-md  text-gray-400 bg-transparent justify-self-center')
            for item in footer_content:
                with ui.row().classes('justify-center'):
                    ui.label(item[0]).classes('text-md  text-gray-400 bg-transparent justify-self-center')
                    ui.link(item[1], item[2])

            [ui.label() for i in range(3)]


    with ui.column().classes('layout-center w-full ui-transition'):

        props_content = 'w-3/4 z-200 align-self-center glass-card-content'

        with ui.card().classes(props_content):
            for i in range(10):
                ui.label('Heellloooo').classes('text-4xl font-bold')

        with ui.card().classes(props_content):
            for i in range(20):
                ui.label('uwu').classes('text-4xl font-bold')

ui.run(
    host='0.0.0.0',
    title='XPlus Studios',
    port=8080,
    dark=True,
    favicon="https://gitlab.com/summersphinx/xplus-games-toolkit/-/raw/main/logo/Icon-white.ico",
    show=False,
    reload=False
)