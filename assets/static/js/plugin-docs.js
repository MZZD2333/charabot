// charabot plugin-docs
'use strict';

import { API } from './api.js';
import './marked.min.js';

let _url = new URL(window.location.href);
const uuid = _url.searchParams.get('uuid');

if (uuid === null) {
    location.assign(location.pathname);
}
else {
    API.pluginData(uuid).then(
        (result) => {
            const root = document.getElementById('root');
            let head = document.createElement('div');
            let icon = document.createElement('img');
            let name = document.createElement('div');
            let docs = document.createElement('div');
            let shadow = docs.attachShadow({ mode: 'open' });
            let l = document.createElement('link');
            let c = document.createElement('body');
            head.className = 'head';
            icon.className = 'icon';
            name.className = 'name';
            docs.className = 'docs';
            icon.alt = '';
            icon.src = `/static/plugin/${uuid}/` + result['icon'];
            name.innerText = result['name'];
            head.setAttribute('stat', result['state'])
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
            root.appendChild(head);
            root.appendChild(docs);
            if (result['docs']) {
                var xhr = new XMLHttpRequest();
                xhr.open('GET', `/static/plugin/${uuid}/` + result['docs']);
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
