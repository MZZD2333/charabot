// charabot plugin-list
'use strict';

import { API } from './api.js';

API.pluginGroupList().then((result) => {
    const data = result.data;
    const root = document.getElementById('root');
    function createGroup(name, plugins) {
        let group = document.createElement('div');
        let title = document.createElement('div');
        let container = document.createElement('div');
        group.className = 'group';
        title.className = 'group-title';
        container.className = 'group-container';
        for (let p of plugins) {
            container.appendChild(createPlugin(p));
        }
        title.setAttribute('name', name);
        group.appendChild(title);
        group.appendChild(container);
        return group;
    }
    function createPlugin(d) {
        let plugin = document.createElement('div');
        let icon = document.createElement('img');
        let info = document.createElement('div');
        let name = document.createElement('div');
        let desc = document.createElement('div');
        let version = document.createElement('div');
        let authors = document.createElement('div');
        plugin.className = 'plugin';
        icon.className = 'icon';
        info.className = 'info';
        name.className = 'name';
        desc.className = 'desc';
        version.className = 'version';
        authors.className = 'authors';
        icon.alt = '';
        icon.src = `/static/plugin/${d.uuid}/${d.icon}`;
        icon.onerror = () => {
            icon.src = '/static/img/plugin-default.webp';
        };
        name.innerHTML = `${d.index}. ${d.name}`;
        desc.innerHTML = d.description;
        version.innerHTML = `version: ${d.version}`;
        authors.innerHTML = `authors: ${d.authors}`;
        plugin.setAttribute('stat', d.state);
        info.appendChild(name);
        info.appendChild(version);
        info.appendChild(desc);
        info.appendChild(authors);
        plugin.appendChild(icon);
        plugin.appendChild(info);
        return plugin;
    }
    let head = document.createElement('div');
    let logo = document.createElement('img');
    let title = document.createElement('div');
    let list = document.createElement('div');
    let chara = document.createElement('img');
    head.className = 'head';
    logo.className = 'logo';
    title.className = 'title';
    list.className = 'list';
    title.innerText = '插件列表';
    logo.src = '/static/img/logo.webp';
    chara.src = '/static/img/chara-v.webp';
    chara.style.position = 'absolute';
    chara.style.width = '30px';
    chara.style.height = '120px';
    chara.style.top = 0;
    chara.style.left = '5px';
    chara.style.opacity = 0.2;
    head.appendChild(logo);
    head.appendChild(title);
    head.appendChild(chara);
    for (let d of data) {
        list.appendChild(createGroup(d.name, d.plugins));
    }
    root.appendChild(head);
    root.appendChild(list);
})