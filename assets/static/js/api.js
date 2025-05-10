// charabot api
'use strict';

const API = {
    request(method, url, body) {
        return new Promise(
            function (resolve, reject) {
                const xhr = new XMLHttpRequest();
                xhr.open(method, url);
                xhr.onload = () => {
                    const data = xhr.response ? JSON.parse(xhr.response) : null;
                    if (200 <= xhr.status < 300) {
                        resolve(data)
                    }
                    else {
                        reject(data);
                    }
                };
                xhr.onerror = () => reject(new Error('Network error'));
                xhr.send(body);
            }
        );
    },
    monitor() {
        var ws = new WebSocket(`ws://${window.location.host}/api/monitor`);
        return ws;
    },
    processList() {
        return this.request('post', '/api/process/list');
    },
    processClose(name) {
        return this.request('post', `/api/process/${name}/close`);
    },
    processStart(name) {
        return this.request('post', `/api/process/${name}/start`);
    },
    processRestart(name) {
        return this.request('post', `/api/process/${name}/restart`);
    },
    pluginList() {
        return this.request('post', '/api/plugin/list');
    },
    pluginData(uuid) {
        return this.request('post', `/api/plugin/${uuid}/data`);
    },
    pluginGroupList() {
        return this.request('post', '/api/plugin/group/list');
    },
    botList() {
        return this.request('post', `/api/bot/list`);
    },
};

export { API }