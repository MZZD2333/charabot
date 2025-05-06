// charabot web-ui
'use strict';

import { API } from './api.js';

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
                this.node.innerHTML = contentHandler();
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
                body: UI.createElement('div', 'con'),
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
        pluginMiniBar() {

        },
    },
};

UI.init();

const page1 = UI.createTabFrame('page-1', document.createElement('a'), '总览');
const p1L = UI.widget.layoutH();
const p1LC1 = UI.widget.layout(1);
const p1LC2 = UI.widget.layout(1);
const p1LC3 = UI.widget.layout(1);
const c1 = UI.widget.card(null, { 'height': '150px', 'flex-shrink': 0 });
const c2 = UI.widget.card(null, { 'height': '250px', 'flex-shrink': 0 });
const c3 = UI.widget.card('进程总览');
const c4 = UI.widget.card(null, { 'height': '150px', 'flex-shrink': 0 });
const c5 = UI.widget.card('插件列表');
const c6 = UI.widget.card(null, { 'height': '150px', 'flex-shrink': 0 });
const c7 = UI.widget.card('BOT列表');
p1LC1.add(c1.root, c2.root, c3.root);
p1LC2.add(c4.root, c5.root);
p1LC3.add(c6.root, c7.root);
p1L.add(p1LC1.root, p1LC2.root, p1LC3.root);
page1.appendChild(p1L.root);

const page2 = UI.createTabFrame('page-2', document.createElement('a'), 'BOT管理');
const page3 = UI.createTabFrame('page-3', document.createElement('a'), '插件管理');
const page4 = UI.createTabFrame('page-4', document.createElement('a'), '进程管理');

UI.tabframe.showPage('page-1');

const ws = API.monitor();
ws.onmessage = (ev) => {
    const data = JSON.parse(ev.data)
    console.log(data);
};