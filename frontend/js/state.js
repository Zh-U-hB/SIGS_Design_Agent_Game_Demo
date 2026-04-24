// state.js — 客户端状态管理（完整实现）
// 职责：基于 sessionStorage 的简单状态存取，用于页面间传递 sessionId、designId 等数据

// 状态存储键名常量
const STATE_KEYS = {
    SESSION_ID: 'sessionId',
    SELECTED_LOCATION: 'selectedLocation',
    SELECTED_EMOTIONS: 'selectedEmotions',
    USER_INPUT: 'userInput',
    TIME_PREFERENCE: 'timePreference',
    ACTIVITY_PREFERENCE: 'activityPreference',
    DESIGN_ID: 'designId',
    CURRENT_DESIGN: 'currentDesign'
};

function setState(key, value) {
    /** 存储状态到 sessionStorage */
    try {
        sessionStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
        console.error('Error setting state:', error);
    }
}

function getState(key) {
    /** 从 sessionStorage 读取状态 */
    const raw = sessionStorage.getItem(key);
    if (raw === null) return null;
    try {
        return JSON.parse(raw);
    } catch {
        return raw;
    }
}

function clearState(key) {
    /** 清除指定状态，不传参则清除全部 */
    if (key) {
        sessionStorage.removeItem(key);
    } else {
        sessionStorage.clear();
    }
}

function getAllState() {
    /** 获取所有状态 */
    const state = {};
    for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        try {
            state[key] = JSON.parse(sessionStorage.getItem(key));
        } catch {
            state[key] = sessionStorage.getItem(key);
        }
    }
    return state;
}

function setMultipleState(stateObj) {
    /** 批量设置状态 */
    Object.entries(stateObj).forEach(([key, value]) => {
        setState(key, value);
    });
}

// 导出给 HTML 页面使用
if (typeof window !== 'undefined') {
    window.STATE_KEYS = STATE_KEYS;
    window.setState = setState;
    window.getState = getState;
    window.clearState = clearState;
    window.getAllState = getAllState;
    window.setMultipleState = setMultipleState;
}

// 导出给其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        STATE_KEYS,
        setState,
        getState,
        clearState,
        getAllState,
        setMultipleState
    };
}
