// charabot widget
'use strict';

const Widget = {
    createElement(tag = 'div', cls = null, id = null, styles = null, attributes = null) {
        const e = document.createElement(tag);
        if (cls != null) {
            e.className = cls;
        }
        if (id != null) {
            e.id = id;
        }
        if (styles != null) {
            for (let k in styles) {
                e.style.setProperty(k, styles[k]);
            }
        }
        if (attributes != null) {
            for (let k in attributes) {
                e.setAttribute(k, attributes[k]);
            }
        }
        return e;
    },
    layout(direction = 0, cls = null, id = null, styles = null, attributes = null) {
        const layout = {
            root: Widget.createElement('div', direction === 0 ? 'flex-h con' : 'flex-v con', id, styles, attributes),
            child: new Array(),
            add(...element) {
                for (let e of element) {
                    this.child.push(e);
                    this.root.appendChild(e);
                }
                this.refresh();
            },
            remove(index) {
                this.root.removeChild(this.child[index]);
                this.refresh();
            },
            refresh() { }
        }
        if (cls !== null) {
            layout.root.classList.add(cls);
        }
        return layout;
    },
    card(title = null, cls = null, id = null, styles = null, attributes = null) {
        const card = {
            root: Widget.createElement(),
            layout: Widget.layout(1, 'card', id, styles, attributes),
            head: {
                root: Widget.createElement(),
                layout: Widget.layout(0, 'head'),
                state: Widget.createElement('div', 'state'),
                title: Widget.createElement('div', 'title fbd-dps'),
            },
            body: Widget.createElement('div', 'body'),
        }
        if (title != null) {
            if (title instanceof HTMLElement) {
                card.head.title.appendChild(title);
            }
            else {
                card.head.title.innerHTML = title;
            }
        }
        if (cls !== null) {
            layout.root.classList.add(cls);
        }
        card.root = card.layout.root;
        card.head.root = card.head.layout.root;
        card.head.layout.add(card.head.state, card.head.title);
        card.layout.add(card.head.root, card.body);
        return card;
    },
}


export { Widget };