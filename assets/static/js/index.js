// charabot index
'use strict';

let _url = new URL(location.href);

function _useCSS(...url) {
    for (let u of url) {
        let l = document.createElement('link');
        l.href = u;
        l.rel = 'stylesheet';
        document.head.appendChild(l);
    }
}
function _clearCSS() {
    document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
        link.parentNode.removeChild(link);
    });
}

_clearCSS();

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
            _useCSS('/static/css/web-ui.css', '/static/css/widget.css');
        });
        break
}
