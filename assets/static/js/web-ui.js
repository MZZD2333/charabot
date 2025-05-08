// charabot web-ui
'use strict';

import { API } from './api.js';
import { SmoothieChart, TimeSeries } from './smoothie.min.js';
import { Widget } from './widget.js';

const UI = {
    root: document.getElementById('root'),
    sidemenu: {
        layout: Widget.layout(1, null, 'side-menu', null, { fold: 0 }),
        list: Widget.createElement('div', 'list con'),
        mask: Widget.createElement('div', 'mask'),
        buttons: {},
        init() {
            const head = Widget.layout(0, 'head');
            const fold = Widget.createElement('div', 'fold');
            const logo = Widget.createElement('img', 'logo fbd-dps');
            const bg = Widget.createElement('img', 'bg');
            fold.innerHTML = '<div></div>'.repeat(3);
            logo.src = '/static/img/chara-h.webp';
            bg.src = '/static/img/chara-bg.webp';
            head.add(fold, logo);
            this.list.appendChild(this.mask);
            this.layout.add(head.root, this.list, bg);
            fold.onclick = () => {
                const f = this.layout.root.getAttribute('fold');
                this.layout.root.setAttribute('fold', f == 0 ? 1 : 0);
                this.layout.root.style.width = f == 0 ? '60px' : '240px';
                UI.tooltips.setContent(f == 0 ? '点击展开' : '点击折叠')
            };
            UI.addTooltips(fold, () => { return this.layout.root.getAttribute('fold') == 0 ? '点击折叠' : '点击展开' });
            UI.root.appendChild(this.layout.root);
        },
        createButton(icon, text) {
            const b = Widget.layout(0, 'btn');
            const i = Widget.createElement('div', 'icon');
            const t = Widget.createElement('div', 'text');
            t.innerText = text;
            b.root.onmouseenter = () => { this.mask.style.top = b.root.offsetTop };
            i.appendChild(icon);
            b.add(i, t);
            this.list.appendChild(b.root);
            return b.root;
        },
    },
    tabframe: {
        root: Widget.createElement('div', 'con', 'tab-frame'),
        pages: new Map(),
        init() { UI.root.appendChild(this.root) },
        createPage(id) {
            let page = Widget.createElement('div', 'page', id);
            this.pages[id] = page;
            this.root.appendChild(page)
            return page;
        },
        showPage(id) {
            for (let n in this.pages) {
                this.pages[n].style.display = n == id ? 'flex' : 'none';
            };
        },
    },
    tooltips: {
        root: Widget.createElement('div', 'fbd-dps', 'tool-tips'),
        hide() {
            this.root.style.opacity = 0;
        },
        show() {
            this.root.style.opacity = 1;
        },
        move(x, y) {
            if (x > document.body.clientWidth / 2) {
                this.root.style.left = x - this.root.offsetWidth - 10;
            }
            else {
                this.root.style.left = x + 10;
            }
            if (y > document.body.clientHeight / 2) {
                this.root.style.top = y - this.root.offsetHeight - 10;
            }
            else {
                this.root.style.top = y + 10;
            }
        },
        setContent(content) {
            if (content !== null) {
                if (content instanceof HTMLElement) {
                    this.root.innerHTML = '';
                    this.root.appendChild(content);
                }
                else if (content instanceof Function) {
                    this.setContent(content());
                }
                else {
                    this.root.innerHTML = content;
                }
            }
            else {
                this.root.innerHTML = '';
            }
        },
        init() { UI.root.appendChild(this.root) },
    },
    popup: {

    },
    init() {
        if (this.root === null) {
            this.root = this.createElement('div', null, 'root');
        }
        this.root.className = 'flex-h con';
        this.root.innerHTML = '';
        this.sidemenu.init();
        this.tabframe.init();
        this.tooltips.init();
    },
    addTooltips(element, content) {
        let n = null;
        element.onmouseenter = () => {
            element.onmousemove = (event) => {
                this.tooltips.move(event.clientX, event.clientY);
            };
            element.onmouseleave = () => {
                if (n !== null) {
                    clearTimeout(n);
                }
                element.onmousemove = null;
                element.onmouseleave = null;
                this.tooltips.hide();
            };
            n = setTimeout(() => {
                clearTimeout(n);
                n = null;
                this.tooltips.setContent(content);
                this.tooltips.show();
            }, 500);
        };
        return element;
    },
    createTabFrame(id, icon, text) {
        let button = this.sidemenu.createButton(icon, text);
        let page = this.tabframe.createPage(id);
        button.onclick = () => { this.tabframe.showPage(id) };
        return page;
    },
}

UI.init()

class Monitor {
    constructor() {
        this.handlers = new Array();
        this.connect();
    }
    connect() {
        this.ws = API.monitor();
        this.ws.onmessage = (ev) => {
            const data = JSON.parse(ev.data);
            for (let handler of this.handlers) {
                handler(data);
            }
        };
        this.ws.onclose = () => {
            setTimeout(this.connect, 3000)
        };
        this.ws.onerror = () => {
            this.ws.close();
        }
    }
    addHandler(handler) {
        this.handlers.push(handler);
    }
}

const monitor = new Monitor();


!function () {
    function botMiniBar() {
    }
    function pluginMiniBar(data) {
        const bar = {
            data: data,
            root: Widget.createElement('div', 'plugin'),
            icon: Widget.createElement('img', 'icon'),
            name: Widget.createElement('div', 'name'),
            update(data) { this.data = data; },
        }
        bar.root.setAttribute('state', data.state);
        bar.icon.src = `/static/plugin/${data.uuid}/${data.icon}`;
        bar.icon.onerror = () => { bar.icon.src = '/static/img/plugin-default.webp' };
        bar.name.innerText = data.name;
        const layout = Widget.layout();
        layout.add(bar.icon);
        layout.add(bar.name);
        bar.root.appendChild(layout.root);
        UI.addTooltips(bar.root, () => { return bar.data.name });
        return bar;
    }
    function processMiniBar() {
        const bar = {
            root: Widget.createElement('div', 'process'),
            name: Widget.createElement('div', 'name'),
            pid: Widget.createElement('div', 'pid'),
            cpu: Widget.createElement('div', 'cpu'),
            mem: Widget.createElement('div', 'mem'),
            async update(name, alive, pid, cpu, mem) {
                this.name.innerText = name;
                this.pid.innerText = pid;
                this.cpu.innerText = cpu;
                this.mem.innerText = mem;
                cpuline.append(Date.now(), cpu);
                memline.append(Date.now(), mem);
            },
        }
        bar.root.appendChild(bar.name);
        bar.root.appendChild(bar.pid);
        bar.root.appendChild(bar.cpu);
        bar.root.appendChild(bar.mem);
        const tooltip = Widget.layout(1);
        const cpucanv = Widget.createElement('canvas');
        const memcanv = Widget.createElement('canvas');
        cpucanv.setAttribute('width', 250);
        cpucanv.setAttribute('height', 50);
        memcanv.setAttribute('width', 250);
        memcanv.setAttribute('height', 50);
        const a = Widget.createElement();
        const b = Widget.createElement();
        a.innerHTML = 'CPU占用';
        b.innerHTML = '内存占用';
        tooltip.add(a, cpucanv, b, memcanv)
        const opt = {
            minValue: 0,
            millisPerPixel: 20,
            grid:
            {
                fillStyle: 'transparent',
                strokeStyle: 'transparent',
                verticalSections: 3,
                borderVisible: false
            },
            labels:
            {
                fillStyle: '#ffffff',
                fontSize: 12,
                precision: 2,
            }
        };
        const cpuchart = new SmoothieChart(opt);
        const memchart = new SmoothieChart(opt);
        const cpuline = new TimeSeries();
        const memline = new TimeSeries();
        cpuchart.addTimeSeries(cpuline, { strokeStyle: 'rgb(0, 137, 228)', lineWidth: 2 });
        memchart.addTimeSeries(memline, { strokeStyle: 'rgb(255, 217, 0)', lineWidth: 2 });
        cpuchart.streamTo(cpucanv, 3000);
        memchart.streamTo(memcanv, 3000);
        UI.addTooltips(bar.root, () => { return tooltip.root; });
        return bar;
    }

    const page = UI.createTabFrame('page-1', document.createElement('a'), '总览');
    const layout = Widget.layout();
    layout.refresh = () => { const n = layout.child.length; for (let e of layout.child) { e.style.width = `calc(100% / ${n})` } };
    const col1 = Widget.layout(1);
    const col2 = Widget.layout(1);
    const col3 = Widget.layout(1);
    const c1 = Widget.card(null, null, null, { 'height': '150px', 'margin-bottom': 0, 'flex-shrink': 0 });
    const c2 = Widget.card('进程总览');
    const c3 = Widget.card(null, null, null, { 'width': '100%', 'height': '150px', 'margin-left': 0, 'margin-right': 0, 'margin-bottom': 0, 'flex-shrink': 0 });
    const c4 = Widget.card('插件列表', null, null, { 'width': '100%', 'margin-left': 0, 'margin-right': 0 });
    const c5 = Widget.card(null, null, null, { 'height': '150px', 'margin-bottom': 0, 'flex-shrink': 0 });
    const c6 = Widget.card('BOT列表');
    col1.add(c1.root, c2.root);
    col2.add(c3.root, c4.root);
    col3.add(c5.root, c6.root);
    layout.add(col1.root, col2.root, col3.root);
    page.appendChild(layout.root);
    API.processList().then((data) => {
        const bars = new Map();
        const main = processMiniBar();
        c2.body.appendChild(main.root);
        main.update(data.main.name, data.main.alive, data.main.pid, data.main.cpu, data.main.mem);
        for (let worker of data.workers) {
            const bar = processMiniBar();
            c2.body.appendChild(bar.root);
            bars[worker.name] = bar;
            bar.update(worker.name, worker.alive, worker.pid, worker.cpu, worker.mem)
        }
        monitor.addHandler((d) => {
            main.update(d.main.name, d.main.alive, d.main.pid, d.main.cpu, d.main.mem);
            for (let worker of d.workers) {
                bars[worker.name].update(worker.name, worker.alive, worker.pid, worker.cpu, worker.mem);
            }
        })
    });
    API.pluginList().then((data) => {
        for (let plugin of data) {
            const bar = pluginMiniBar(plugin);
            c4.body.appendChild(bar.root);
        }
    });
}();
