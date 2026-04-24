export class EventBus {
    constructor() {
        this._listeners = {};
    }

    on(event, callback) {
        if (!this._listeners[event]) {
            this._listeners[event] = [];
        }
        this._listeners[event].push(callback);
        return this;
    }

    off(event, callback) {
        if (!this._listeners[event]) return this;
        this._listeners[event] = this._listeners[event].filter(cb => cb !== callback);
        return this;
    }

    emit(event, data) {
        if (!this._listeners[event]) return this;
        for (const cb of this._listeners[event]) {
            cb(data);
        }
        return this;
    }

    removeAll() {
        this._listeners = {};
    }
}
