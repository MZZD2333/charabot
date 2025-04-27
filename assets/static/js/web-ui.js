// charabot web-ui
'use strict';

const API = {
    request(method, url, body) {
        return new Promise(
            function (resolve, reject) {
                var xhr = new XMLHttpRequest();
                xhr.open(method, url);
                xhr.onload = () => {
                    if (xhr.status === 200) {
                        resolve(xhr.response);
                    } else {
                        reject(xhr.response);
                    }
                };
                xhr.onerror = () => reject(new Error('Network error'));
                xhr.send(body);
            }
        );
    },
    monitor(){
        console.log(window.location.host);
        var ws = new WebSocket(`ws://${window.location.host}/monitor`);
        return ws;

    },
    pluginList() {
        return this.request('post', '/api/plugin/list');
    },
    pluginGroupReload(name) {
        return this.request('post', `/api/plugin/group/${name}/reload`);
    },
    botList() {
        return this.request('post', `/api/bot/list`);
    },
};

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
            var head = document.createElement('div');
            var logo = document.createElement('div');
            var toggle = document.createElement('button');
            head.className = 'side-menu-head';
            logo.className = 'side-menu-head-logo';
            toggle.className = 'side-menu-head-toggle';
            toggle.innerHTML = '<div></div><div></div><div></div>';
            this.node.setAttribute('mode', 1);
            toggle.onclick = (event) => {
                if (this.node.getAttribute('mode') == 1) {
                    this.node.setAttribute('mode', 0);
                    logo.style.display = 'none';
                    this.node.style.width = '60px';
                    UI.tabframe.node.style.width = 'calc(100% - 60px)';
                    UI.tabframe.node.style.left = '60px';
                }
                else {
                    this.node.setAttribute('mode', 1);
                    logo.style.display = 'block';
                    this.node.style.width = '240px';
                    UI.tabframe.node.style.width = 'calc(100% - 240px)';
                    UI.tabframe.node.style.left = '240px';
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
            head.appendChild(logo);
            this.node.appendChild(head);
            this.list.appendChild(this.mask);
            this.node.appendChild(this.list);
            UI.root.appendChild(this.node);
        },
        addButton(icon, text) {
            var button = document.createElement('button');
            var btnicon = document.createElement('div');
            var btntext = document.createElement('div');
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
            var page = document.createElement('div');
            page.className = 'tab-frame-page';
            this.pages[name] = page;
            this.node.appendChild(page)
            return page;
        },
        showPage(name) {
            for (var n in this.pages) {
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
            this.node.innerHTML = contentHandler();
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
        var button = this.sidemenu.addButton(icon, text);
        var page = this.tabframe.addPage(name);
        button.onclick = (event) => {
            this.tabframe.showPage(name);
        };
        return page;
    }
};

UI.init();

var page1 = UI.createTabFrame('1', document.createElement('a'), '总览');
var page2 = UI.createTabFrame('2', document.createElement('a'), 'BOT管理');
var page3 = UI.createTabFrame('3', document.createElement('a'), '插件管理');
var page4 = UI.createTabFrame('4', document.createElement('a'), '进程管理');



UI.tabframe.showPage('1');
