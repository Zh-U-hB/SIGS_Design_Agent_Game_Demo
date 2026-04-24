import { worldToScreen } from '../utils/coordinate.js';

export class TooltipManager {
    constructor(container, language = 'zh') {
        this._container = container;
        this._language = language;

        this._el = document.createElement('div');
        this._el.className = 'engine-tooltip';
        container.appendChild(this._el);
    }

    show(text, screenPosition) {
        this._el.textContent = text;
        this._el.style.left = `${screenPosition.x}px`;
        this._el.style.top = `${screenPosition.y}px`;
        this._el.classList.add('visible');
    }

    hide() {
        this._el.classList.remove('visible');
    }

    setLanguage(lang) {
        this._language = lang;
    }

    destroy() {
        if (this._el.parentNode) {
            this._el.parentNode.removeChild(this._el);
        }
    }
}
