// charabot plugin-list
'use strict';

import { API } from './api.js';


API.pluginList().then((result) => {
    document.body.innerText = result;
})