// charabot plugin-docs
'use strict';

import { API } from './api.js';
import './marked.min.js';

const _url = new URL(window.location.href);
const uuid = _url.searchParams.get('uuid');

if (uuid === null) {
    location.assign(location.pathname);
}
else {
    API.pluginData(uuid).then(
        (result) => {
            const data = result.data;
            const root = document.getElementById('root');
            let head = document.createElement('div');
            let icon = document.createElement('img');
            let name = document.createElement('div');
            let docs = document.createElement('div');
            let shadow = docs.attachShadow({ mode: 'open' });
            let chara = document.createElement('img');
            chara.src = '/static/img/chara-v.webp';
            chara.style.position = 'absolute';
            chara.style.width = '30px';
            chara.style.height = '120px';
            chara.style.top = 0;
            chara.style.left = '5px';
            chara.style.opacity = 0.2;
            let l = document.createElement('link');
            let c = document.createElement('body');
            head.className = 'head';
            icon.className = 'icon';
            name.className = 'name';
            docs.className = 'docs';
            icon.alt = '';
            icon.src = `/static/plugin/${uuid}/${data.icon}`;
            icon.onerror = () => {
                icon.src = '/static/img/plugin-default.webp'
            };
            name.innerText = data.name;
            head.setAttribute('stat', data.state)
            l.href = '/static/css/markdown.css';
            l.rel = 'stylesheet';
            c.style.position = 'relative';
            c.style.display = 'block';
            c.style.width = '100%';
            c.style.height = 'auto';
            shadow.appendChild(l);
            shadow.appendChild(c);
            head.appendChild(icon);
            head.appendChild(name);
            head.appendChild(chara);
            root.appendChild(head);
            root.appendChild(docs);
            if (data.docs) {
                const xhr = new XMLHttpRequest();
                xhr.open('GET', `/static/plugin/${uuid}/${data.docs}`);
                xhr.onload = () => {
                    if (xhr.status === 200) {
                        c.innerHTML = marked.parse(xhr.response);
                    }
                };
                xhr.onerror = () => reject(new Error('Network error'));
                xhr.send();
            }
        }
    )
}
