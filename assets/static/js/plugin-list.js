// charabot plugin-list
'use strict';

import { API } from './api.js';


API.pluginList().then((result) => {
    const root = document.getElementById('root');
    function createGroup(name, data) {
        var group = document.createElement('div');
        group.className = 'group';
        for (var i in data) {
            group.appendChild(createRow(data[i]));
        }
        return group;
    }
    function createRow(data) {
        var row = document.createElement('div');
        var icon = document.createElement('div');
        var info = document.createElement('div');
        var stat = document.createElement('div');
        row.className = 'row';
        icon.className = 'icon';
        info.className = 'info';
        stat.className = 'stat';
        row.appendChild(icon);
        row.appendChild(info);
        row.appendChild(stat);
        return row;
    }
    var head = document.createElement('div');
    var list = document.createElement('div');
    head.className = 'head';
    list.className = 'list';
    var groups = new Map();
    for (var i in result) {
        var name = result[i].group;
        if (name in groups) {
            groups[name].push(result[i])
        }
        else {
            groups[name] = new Array();
            groups[name].push(result[i])
        }
    }
    for (var name in groups) {
        list.appendChild(createGroup(name, groups[name]));
    }
    root.appendChild(head);
    root.appendChild(list);
})