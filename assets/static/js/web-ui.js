// charabot web-ui
'use strict';

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
            let toggle = document.createElement('button');
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
                    UI.tooltips.setContent('点击折叠');
                }
                else {
                    this.node.setAttribute('mode', 1);
                    this.node.style.width = '240px';
                    UI.tabframe.node.style.width = 'calc(100% - 240px)';
                    UI.tabframe.node.style.left = '240px';
                    UI.tooltips.setContent('点击展开');
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
        addPage(name) {
            let page = document.createElement('div');
            page.className = 'tab-frame-page';
            this.pages[name] = page;
            this.node.appendChild(page)
            return page;
        },
        showPage(name) {
            for (let n in this.pages) {
                if (n == name) {
                    this.pages[n].style.display = 'block';
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
            if (contentHandler != null){
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

    createTabFrame(name, icon, text) {
        let button = this.sidemenu.addButton(icon, text);
        let page = this.tabframe.addPage(name);
        button.onclick = (event) => {
            this.tabframe.showPage(name);
        };
        return page;
    }
};

UI.init();

let page1 = UI.createTabFrame('1', document.createElement('a'), '总览');
let page2 = UI.createTabFrame('2', document.createElement('a'), 'BOT管理');
let page3 = UI.createTabFrame('3', document.createElement('a'), '插件管理');
let page4 = UI.createTabFrame('4', document.createElement('a'), '进程管理');



UI.tabframe.showPage('1');
