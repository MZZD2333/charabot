// charabot api
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
        var ws = new WebSocket(`ws://${window.location.host}/monitor`);
        return ws;

    },
    pluginList() {
        return this.request('post', '/api/plugin/list');
    },
    pluginData(uuid) {
        return this.request('post', `/api/plugin/${uuid}/data`);
    },
    pluginGroupReload(name) {
        return this.request('post', `/api/plugin/group/${name}/reload`);
    },
    botList() {
        return this.request('post', `/api/bot/list`);
    },
};

export {API}