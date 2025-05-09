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
                this.pages[n].style.display = n == id ? 'block' : 'none';
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
                element.onmousemove = undefined;
                element.onmouseleave = undefined;
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
};

UI.init();

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
};

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
        const data = {
            name: '',
            busy: 0,
        };
        const bar = {
            data: new Map(),
            layout: Widget.layout(0, 'process', null, null, { alive: 0, busy: 0 }),
            name: Widget.createElement('div', 'name'),
            pid: Widget.createElement('div', 'pid'),
            cpu: Widget.createElement('div', 'cpu'),
            mem: Widget.createElement('div', 'mem'),
            fold: {
                layout: Widget.layout(0, 'fold', null, { 'opacity': 0, 'pointer-events': 'none' }),
                state: Widget.createElement('div', 'state'),
                close: Widget.createElement('div', 'close'),
                start: Widget.createElement('div', 'start'),
                restart: Widget.createElement('div', 'restart'),
            },
            async update(name, alive, pid, cpu, mem) {
                data.name = name;
                this.layout.root.setAttribute('alive', alive ? 1 : 0)
                this.name.innerText = name;
                this.pid.innerText = pid;
                this.cpu.innerText = cpu;
                this.mem.innerText = mem;
                cpuline.append(Date.now(), cpu);
                memline.append(Date.now(), mem);
            },
        }
        function reset() {
            console.log(23333)
            data.busy = 0;
            bar.layout.root.setAttribute('busy', 0);
            bar.fold.state.innerText = '请选择操作';
        };
        reset();
        bar.fold.close.onclick = () => {
            if (!data.busy) {
                data.busy = 1;
                bar.layout.root.setAttribute('busy', 1);
                API.processReload(data.name).then(reset);
                bar.fold.state.innerText = '关闭进程中';
            }
        };
        bar.fold.start.onclick = () => {
            if (!data.busy) {
                data.busy = 1;
                bar.layout.root.setAttribute('busy', 1);
                API.processReload(data.name).then(reset);
                bar.fold.state.innerText = '开启进程中';
            }
        };
        bar.fold.restart.onclick = () => {
            if (!data.busy) {
                data.busy = 1;
                bar.layout.root.setAttribute('busy', 1);
                API.processReload(data.name).then(reset);
                bar.fold.state.innerText = '重启进程中';
            }
        };
        bar.layout.root.onclick = () => {
            bar.fold.layout.root.style.opacity = 1;
            bar.fold.layout.root.style.pointerEvents = 'auto';
            bar.layout.root.onmouseenter = undefined;
            bar.layout.root.onmousemove = undefined;

            UI.addTooltips(bar.fold.close, () => { return '关闭' });
            UI.addTooltips(bar.fold.start, () => { return '开启' });
            UI.addTooltips(bar.fold.restart, () => { return '重启' });
            UI.tooltips.hide();
            bar.fold.layout.root.onmouseleave = () => {
                bar.fold.layout.root.style.opacity = 0;
                bar.fold.layout.root.style.pointerEvents = 'none';
                UI.addTooltips(bar.layout.root, () => { return tooltip.root });
            };
            setTimeout(() => { UI.tooltips.hide() }, 500);
        };
        bar.layout.root.classList.toggle('con');
        bar.fold.layout.add(bar.fold.restart, bar.fold.close, bar.fold.start, bar.fold.state);
        bar.layout.add(bar.name, bar.pid, bar.cpu, bar.mem, bar.fold.layout.root);
        const tooltip = Widget.layout(1);
        const cpucanv = Widget.createElement('canvas', null, null, { 'margin-bottom': '5px' }, { width: 250, height: 50 });
        const memcanv = Widget.createElement('canvas', null, null, null, { width: 250, height: 50 });
        tooltip.add(cpucanv, memcanv)
        const opt = {
            minValue: 0,
            yRangeFunction(data) {
                data.min -= 0.5;
                data.max += 0.5;
                return data;
            },
            yMinFormatter(min, prc) { return '0' },
            yMaxFormatter(max, prc) { return parseFloat(max - 0.5).toFixed(prc) },
            millisPerPixel: 30,
            grid: {
                fillStyle: 'transparent',
                strokeStyle: 'transparent',
                borderVisible: false
            },
            labels: {
                fillStyle: 'rgba(255, 255, 255, 0.8)',
                fontSize: 12,
                precision: 2,
            },
        };
        const topt = {
            fillStyle: 'rgba(255, 255, 255, 0.8)',
            fontSize: 12,
            fontFamily: 'monospace',
            verticalAlign: 'bottom'
        };
        const cpuchart = new SmoothieChart({ title: { text: 'CPU (%)', ...topt }, ...opt });
        const memchart = new SmoothieChart({ title: { text: 'RAM (MB)', ...topt }, ...opt });
        const cpuline = new TimeSeries();
        const memline = new TimeSeries();
        cpuchart.addTimeSeries(cpuline, { strokeStyle: 'rgb(0, 137, 228)', lineWidth: 1, fillStyle: 'rgba(0, 137, 228, 0.1)' });
        memchart.addTimeSeries(memline, { strokeStyle: 'rgb(255, 217, 0)', lineWidth: 1, fillStyle: 'rgba(255, 217, 0, 0.1)' });
        cpuchart.streamTo(cpucanv, 1000);
        memchart.streamTo(memcanv, 1000);
        UI.addTooltips(bar.layout.root, () => { return tooltip.root });
        return bar;
    }
    const icon = Widget.createElement('div', 'con', null, { 'color': 'rgb(175, 175, 175)', 'line-height': '36px', 'font-family': 'icon', 'font-size': '24px', 'text-align': 'center' });
    icon.innerText = '\uF3F4';
    const page = UI.createTabFrame('page-1', icon, '总览');
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
        const layout = Widget.layout(1, 'process-list');
        layout.root.classList.toggle('con');
        main.layout.root.onclick = undefined;
        c2.body.appendChild(layout.root);
        layout.add(main.layout.root);
        main.update(data.main.name, data.main.alive, data.main.pid, data.main.cpu, data.main.mem);
        for (let worker of data.workers) {
            const bar = processMiniBar();
            layout.add(bar.layout.root);
            bars[worker.name] = bar;
            bar.update(worker.name, worker.alive, worker.pid, worker.cpu, worker.mem)
        }
        monitor.addHandler((d) => {
            main.update(d.main.name, d.main.alive, d.main.pid, d.main.cpu, d.main.mem);
            for (let worker of d.workers) {
                if (worker.alive) {
                    bars[worker.name].update(worker.name, worker.alive, worker.pid, worker.cpu, worker.mem);
                }
                else {
                    bars[worker.name].update(worker.name, 0, '--', 0, 0);
                }
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
