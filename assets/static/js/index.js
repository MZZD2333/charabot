// charabot index
'use strict';

let _url = new URL(location.href);

function _useCSS(url) {
    let l = document.createElement('link');
    l.href = url;
    l.rel = 'stylesheet';
    document.head.appendChild(l);
}

switch (_url.searchParams.get('mode')) {
    case 'plugin-list':
        import('./plugin-list.js').then(() => {
            _useCSS('/static/css/plugin-list.css');
        });
        break
    case 'plugin-docs':
        import('./plugin-docs.js').then(() => {
            _useCSS('/static/css/plugin-docs.css');
        });
        break
    case null:
        import('./web-ui.js').then(() => {
            _useCSS('/static/css/web-ui.css');
        });
        break
}
