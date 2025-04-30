// charabot plugin-docs
'use strict';

import { API } from './api.js';

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
            let icon = document.createElement('div');
            let name = document.createElement('div');
            let stat = document.createElement('div');
            let docs = document.createElement('div');
            let s = document.createElement('style');
            let m = document.createElement('div');

            docs.appendChild(s);
            docs.appendChild(m);

            root.appendChild(head);
            root.appendChild(docs);
        }
    )

}
