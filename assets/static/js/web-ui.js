// charabot web-ui
'use strict';

import { API } from './api.js';
import { SmoothieChart, TimeSeries } from './smoothie.min.js';

const UI = {
    root: document.getElementById('root'),
    sidemenu: {
        node: document.createElement('div'),
        list: document.createElement('div'),
        mask: document.createElement('div'),
        buttons: {},
        init() {
            this.node.innerHTML = '';
            this.node.className = 'side-menu';
            this.list.className = 'side-menu-list';
            this.mask.className = 'side-menu-mask';
            let head = document.createElement('div');
            let title = document.createElement('img');
            let toggle = document.createElement('div');
            let bg = document.createElement('img');
            head.className = 'side-menu-head';
            title.className = 'side-menu-head-title';
            bg.className = 'side-menu-bg';
            title.src = '/static/img/chara-h.webp';
            bg.src = '/static/img/chara-bg.webp';
            toggle.className = 'side-menu-head-toggle';
            toggle.innerHTML = '<div></div><div></div><div></div>';
            this.node.setAttribute('mode', 1);
            toggle.onclick = (event) => {
                if (this.node.getAttribute('mode') == 1) {
                    this.node.setAttribute('mode', 0);
                    this.node.style.width = '60px';
                    UI.tabframe.node.style.width = 'calc(100% - 60px)';
                    UI.tabframe.node.style.left = '60px';
                    UI.tooltips.setContent('点击展开');
                }
                else {
                    this.node.setAttribute('mode', 1);
                    this.node.style.width = '240px';
                    UI.tabframe.node.style.width = 'calc(100% - 240px)';
                    UI.tabframe.node.style.left = '240px';
                    UI.tooltips.setContent('点击折叠');
                }
            };
            UI.addTooltips(toggle, function () {
                if (UI.sidemenu.node.getAttribute('mode') == 1) {
                    return '点击折叠';
                }
                else {
                    return '点击展开';
                }
            });
            head.appendChild(toggle);
            head.appendChild(title);
            this.node.appendChild(head);
            this.list.appendChild(this.mask);
            this.node.appendChild(this.list);
            this.node.appendChild(bg);
            UI.root.appendChild(this.node);
        },
        addButton(icon, text) {
            let button = document.createElement('button');
            let btnicon = document.createElement('div');
            let btntext = document.createElement('div');
            button.className = 'side-menu-button';
            btnicon.className = 'side-menu-button-icon';
            btntext.className = 'side-menu-button-text';
            btntext.innerText = text;
            button.onmouseenter = (event) => {
                this.mask.style.top = button.offsetTop;
            };
            btnicon.appendChild(icon);
            button.appendChild(btnicon);
            button.appendChild(btntext);
            this.list.appendChild(button);
            return button;
        },
    },
    tabframe: {
        node: document.createElement('div'),
        pages: {},
        init() {
            this.node.innerHTML = '';
            this.node.className = 'tab-frame';
            UI.root.appendChild(this.node);
        },
        addPage(id) {
            let page = document.createElement('div');
            page.className = 'tab-frame-page';
            page.id = id;
            this.pages[id] = page;
            this.node.appendChild(page)
            return page;
        },
        showPage(id) {
            for (let n in this.pages) {
                if (n == id) {
                    this.pages[n].style.display = 'flex';
                }
                else {
                    this.pages[n].style.display = 'none';
                }
            };
        },
    },
    tooltips: {
        node: document.createElement('div'),
        hide() {
            this.node.innerHTML = '';
            this.node.style.display = 'none';
        },
        show(contentHandler) {
            if (contentHandler != null) {
                const content = contentHandler();
                if (content instanceof HTMLElement) {
                    this.node.innerHTML = '';
                    this.node.appendChild(content);
                }
                else {
                    this.node.innerHTML = contentHandler();
                }
            }
            this.node.style.display = 'block';
        },
        move(x, y) {
            if (x > document.body.clientWidth / 2) {
                this.node.style.left = x - this.node.offsetWidth - 10;
            }
            else {
                this.node.style.left = x + 10;
            }
            if (y > document.body.clientHeight / 2) {
                this.node.style.top = y - this.node.offsetHeight - 10;
            }
            else {
                this.node.style.top = y + 10;
            }
        },
        setContent(content) {
            this.node.innerHTML = content;
        },
        init() {
            this.node.innerHTML = '';
            this.node.className = 'tooltips';
            UI.root.appendChild(this.node);
        },
    },
    init() {
        this.root.innerHTML = '';
        this.sidemenu.init();
        this.tabframe.init();
        this.tooltips.init();
    },
    addTooltips(element, contentHandler) {
        element.onmouseenter = (event) => {
            this.tooltips.show(contentHandler);
        };
        element.onmousemove = (event) => {
            this.tooltips.move(event.clientX, event.clientY);
        };
        element.onmouseleave = (event) => {
            this.tooltips.hide();
        };
        return element;
    },
    createTabFrame(id, icon, text) {
        let button = this.sidemenu.addButton(icon, text);
        let page = this.tabframe.addPage(id);
        button.onclick = (event) => {
            this.tabframe.showPage(id);
        };
        return page;
    },
    createElement(tag, cls = null, id = null) {
        const e = document.createElement(`${tag}`);
        if (cls != null) {
            e.className = cls;
        }
        if (id != null) {
            e.id = id;
        }
        return e;
    },
    widget: {
        layout(direction = 0) {
            const layout = {
                root: UI.createElement('div', 'con'),
                child: new Array(),
                add(...element) {
                    for (let e of element) {
                        this.child.push(e);
                        this.root.appendChild(e);
                    }
                    this._refresh();
                },
                remove(index) {
                    this.root.removeChild(this.child[index]);
                    this._refresh();
                },
                _refresh() { }
            }
            if (direction === 0) {
                layout.root.classList.add('flex-h');
            }
            else if (direction === 1) {
                layout.root.classList.add('flex-v');
            }
            return layout;
        },
        layoutH(col = 0) {
            const layout = this.layout(0);
            layout._refresh = () => {
                const n = layout.child.length;
                for (let e of layout.child) {
                    e.style.width = `calc(100% / ${n})`;
                }
            };
            for (let i = 0; i < col; i++) {
                const con = UI.createElement('div', 'con');
                con.style.width = `calc(100% / ${col})`;
                layout.add(con);
            }
            return layout;
        },
        layoutV(row = 0) {
            const layout = this.layout(1);
            layout._refresh = () => {
                const n = layout.child.length;
                for (let e of layout.child) {
                    e.style.height = `calc(100% / ${n})`;
                }
            };
            for (let i = 0; i < row; i++) {
                const con = UI.createElement('div', 'con');
                con.style.height = `calc(100% / ${row})`;
                layout.add(con);
            }
            return layout;
        },
        card(head = null, styles = null) {
            const card = {
                root: UI.createElement('div', 'card'),
                head: null,
                body: UI.createElement('div', 'card-body'),
            }
            if (head != null) {
                card.root.classList.add('flex-v');
                card.head = UI.createElement('div', 'card-head');
                card.head.classList.add('flex-h');
                const con = UI.createElement('div', 'con');
                if (head instanceof HTMLElement) {
                    con.appendChild(head);
                }
                else {
                    con.innerHTML = head;
                }
                card.head.appendChild(con);
                card.root.appendChild(card.head);
            }
            card.root.appendChild(card.body);
            if (styles != null) {
                for (let k in styles) {
                    card.root.style.setProperty(k, styles[k]);
                }
            }
            return card;
        },
        botBar() {

        },
        botMiniBar() {
        },
        pluginBar() {

        },
        pluginMiniBar(data) {
            const bar = {
                data: data,
                root: UI.createElement('div', 'plugin-mini-bar'),
                icon: UI.createElement('img', 'plugin-mini-bar-icon'),
                name: UI.createElement('div', 'plugin-mini-bar-name'),
                update(data) {
                    this.data = data;
                },
            }
            bar.root.setAttribute('state', data.state);
            bar.icon.src = `/static/plugin/${data.uuid}/${data.icon}`;
            bar.icon.onerror = () => {
                bar.icon.src = '/static/img/plugin-default.webp';
            };
            bar.name.innerText = data.name;
            const layout = UI.widget.layout();
            layout.add(bar.icon);
            layout.add(bar.name);
            bar.root.appendChild(layout.root);
            UI.addTooltips(bar.root, () => {
                return bar.data.name;
            });
            return bar;
        },
        processBar() {

        },
        processMiniBar() {
            const bar = {
                root: UI.createElement('div', 'process-mini-bar'),
                name: UI.createElement('div', 'process-mini-bar-name'),
                pid: UI.createElement('div', 'process-mini-bar-pid'),
                cpu: UI.createElement('div', 'process-mini-bar-cpu'),
                mem: UI.createElement('div', 'process-mini-bar-mem'),
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
            const tooltip = UI.widget.layout(1);
            const cpucanv = UI.createElement('canvas');
            const memcanv = UI.createElement('canvas');
            cpucanv.style.width = '300px';
            cpucanv.style.height = '150px';
            memcanv.style.width = '300px';
            memcanv.style.height = '150px';
            tooltip.add(cpucanv, memcanv)
            const opt = {
                minValue: 0,
                maxValueScale: 1.05,
                minValueScale: 0.95,
                millisPerPixel: 20,
                grid:
                {
                    fillStyle: 'transparent',
                    strokeStyle: 'transparent',
                    millisPerLine: 1000,
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
            cpuchart.addTimeSeries(cpuline, { strokeStyle: 'rgb(0, 137, 228)', lineWidth: 1 });
            memchart.addTimeSeries(memline, { strokeStyle: 'rgb(255, 217, 0)', lineWidth: 1 });
            cpuchart.streamTo(cpucanv, 3000);
            memchart.streamTo(memcanv, 3000);
            UI.addTooltips(bar.root, () => {
                return tooltip.root;
            });
            return bar;
        },
    },
};

UI.init();

class Monitor {
    constructor() {
        this.handlers = new Array();
        this.connetc();
    }
    connetc() {
        this.ws = API.monitor();
        this.ws.onmessage = (ev) => {
            const data = JSON.parse(ev.data);
            for (let handler of this.handlers) {
                handler(data);
            }
        };
        this.ws.onclose = () => {
            setTimeout(this.connetc, 3000)
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
    const page1 = UI.createTabFrame('page-1', document.createElement('a'), '总览');
    const p1L0 = UI.widget.layoutH();
    const p1L1 = UI.widget.layout(1);
    const p1L2 = UI.widget.layout(1);
    const p1L3 = UI.widget.layout(1);
    const c1 = UI.widget.card(null, { 'height': '150px', 'flex-shrink': 0 });
    const c2 = UI.widget.card(null, { 'height': '250px', 'flex-shrink': 0 });
    const c3 = UI.widget.card('进程总览');
    const c4 = UI.widget.card(null, { 'width': '100%', 'height': '150px', 'margin-left': 0, 'margin-right': 0, 'flex-shrink': 0 });
    const c5 = UI.widget.card('插件列表', { 'width': '100%', 'margin-left': 0, 'margin-right': 0 });
    const c6 = UI.widget.card(null, { 'height': '150px', 'flex-shrink': 0 });
    const c7 = UI.widget.card('BOT列表');
    p1L1.add(c1.root, c2.root, c3.root);
    p1L2.add(c4.root, c5.root);
    p1L3.add(c6.root, c7.root);
    p1L0.add(p1L1.root, p1L2.root, p1L3.root);
    page1.appendChild(p1L0.root);
    API.processList().then((data) => {
        const bars = new Map();
        const main = UI.widget.processMiniBar();
        c3.body.appendChild(main.root);
        main.update(data.main.name, data.main.alive, data.main.pid, data.main.cpu, data.main.mem);
        for (let worker of data.workers) {
            const bar = UI.widget.processMiniBar();
            c3.body.appendChild(bar.root);
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
            const bar = UI.widget.pluginMiniBar(plugin);
            c5.body.appendChild(bar.root);
        }
    });
}();

const page2 = UI.createTabFrame('page-2', document.createElement('a'), '进程管理');
const page3 = UI.createTabFrame('page-3', document.createElement('a'), '插件管理');
const page4 = UI.createTabFrame('page-4', document.createElement('a'), 'BOT管理');

UI.tabframe.showPage('page-1');

