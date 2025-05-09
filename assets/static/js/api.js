// charabot api
'use strict';

const API = {
    request(method, url, body) {
        return new Promise(
            function (resolve, reject) {
                const xhr = new XMLHttpRequest();
                xhr.open(method, url);
                xhr.onload = () => {
                    if (xhr.status === 200) {
                        resolve(JSON.parse(xhr.response));
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
        var ws = new WebSocket(`ws://${window.location.host}/api/process/monitor`);
        return ws;
    },
    processList() {
        return this.request('post', '/api/process/list');
    },
    processReload(name) {
        return this.request('post', `/api/process/${name}/reload`);
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

export {API}