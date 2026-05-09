from nicegui import ui


CANVAS_HTML = '''
<canvas id="fractal-canvas" style="
    position:fixed;inset:0;z-index:0;
    width:100vw;height:100vh;
    background:#050510;
"></canvas>
<div id="fractal-label" style="
    position:fixed;bottom:2rem;left:50%;transform:translateX(-50%);
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
        ['#00ffe7','#00c9ff','#7b2fff'],
        ['#ffe066','#ff6f3c','#ff2d78'],
        ['#a8ff78','#48ff9a','#00b4d8'],
        ['#ff61d2','#fe9090','#7b61ff']
    ];
    var NAMES = ['Sierpinski Triangle','Koch Snowflake','Fractal Tree','Dragon Curve'];

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

    var BUILDERS = [buildSierpinski, buildKoch, buildTree, buildDragon];

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

        var pal = PALETTES[fractalIdx];
        setLabel(NAMES[fractalIdx]);
        var rawTasks = BUILDERS[fractalIdx](pal);
        fractalIdx = (fractalIdx + 1) % 4;

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
            width: 75%; text-align: center;
            box-shadow: 0 8px 40px rgba(0,0,0,.55), inset 0 1px 0 rgba(255,255,255,.1);
        }
        .glass-card-bar {
            background: rgba(255,255,255,.045);
            border: 1px solid rgba(255,255,255,.12);
            backdrop-filter: blur(18px) saturate(160%);
            -webkit-backdrop-filter: blur(18px) saturate(160%);
            border-radius: 1.0rem; padding: 0.8rem 3.2rem;
            width: 80%; text-align: center;
            box-shadow: 0 8px 40px rgba(0,0,0,.55), inset 0 1px 0 rgba(255,255,255,.1);
        }
        .card-title { font-size: 2.4rem; font-weight: 600; letter-spacing:.06em; color:#fff; margin-bottom:.6rem; }
        .card-sub   { font-size:.95rem; font-weight:300; letter-spacing:.12em; color:rgba(180,200,255,.7); margin-bottom:2rem; }
        .card-btn {
            padding:.65rem 2rem; border-radius:999px;
            border:1px solid rgba(255,255,255,.22); background:rgba(255,255,255,.08);
            color:#fff; font-family:'Share Tech Mono',monospace; font-size:.8rem;
            letter-spacing:.2em; cursor:pointer; transition:background .2s;
        }
        .card-btn:hover { background:rgba(255,255,255,.18); }
    </style>
    ''')

    # Canvas goes into body_html — placed before #app in the template,
    # so it exists in the DOM before Vue mounts.
    ui.add_body_html(CANVAS_HTML)

    ui.html('<div id="vignette"></div>')

    with ui.header().classes('glass-card-bar justify-self-center'):
        with ui.button(on_click=lambda: ui.notify('Home')).classes('grow h-full').props('flat'):
            ui.image('https://gitlab.com/summersphinx/xplus-games-toolkit/-/raw/main/logo/xplus2.png').props('fit=scale-down').classes('h-16')
        ui.button('About', on_click=lambda: ui.notify('About')).classes('grow h-full text-2xl text-bold').props('flat')

    with ui.footer(fixed=False).classes('bg-transparent w-full h-16 items-center'):
        footer_content = [
            ["Created with ", "NiceGUI", "https://nicegui.io"],
            ["Hosted on ", "Railway.app", "https://railway.app/"],
        ]
        ui.label('© 2026 X+ Studios. All rights reserved.').classes('text-md  text-gray-400 bg-transparent')
        for item in footer_content:
            with ui.row():
                ui.label(item[0])
                ui.link(item[1], item[2])

    with ui.column().classes('layout-center w-full'):
        with ui.card().classes('w-3/4 z-200 align-self-center glass-card-content'):
            for i in range(10):
                ui.label('Heellloooo').classes('text-4xl font-bold')

        with ui.card().classes('w-3/4 z-200 align-self-center glass-card-content'):
            for i in range(20):
                ui.label('uwu').classes('text-4xl font-bold')

ui.run(
    host='0.0.0.0',
    title='XPlus Studios',
    port=8080,
    dark=True,
    favicon="https://gitlab.com/summersphinx/xplus-games-toolkit/-/raw/main/logo/Icon-white.png",
    show=False,
    reload=False
)

