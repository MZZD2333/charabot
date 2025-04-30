// charabot index
'use strict';

let _url = new URL(location.href);
switch (_url.searchParams.get('mode')) {
    case 'plugin-list':
        import('./plugin-list.js').then((_m) => { });
        break
    case 'plugin-docs':
        import('./plugin-docs.js').then((_m) => { });
        break
    case null:
        import('./web-ui.js').then((_m) => { });
        break
}
