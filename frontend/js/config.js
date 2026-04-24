// config.js — 前端全局配置（完整实现）
// 职责：定义 API 地址、页面路径常量、情绪标签配置、状态管理

// API 配置
// 开发环境：后端运行在 8989 端口
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? `http://localhost:8989/api/v1`
    : `${window.location.origin}/api/v1`;

const API_KEY = localStorage.getItem('api_key') || '';

// 页面路由定义
const PAGES = {
    LANDING: "landing.html",      // 阶段一：进入与吸引
    EXPLORE: "explore.html",      // 阶段二：场景漫游选点
    CREATE: "create.html",        // 阶段三：创意输入
    CONFIRM: "confirm.html",      // 阶段四：确认设计说明
    GENERATE: "generate.html",    // 阶段五：生成与呈现
    GALLERY: "gallery.html"       // 阶段六：社区沉淀
};

// 情绪标签配置
const EMOTION_TAGS = [
    { emoji: "🧍", label: "太拥挤", value: "crowded" },
    { emoji: "📄", label: "太单调", value: "boring" },
    { emoji: "🌿", label: "想要绿色", value: "green" },
    { emoji: "☀️", label: "采光不好", value: "dark" },
    { emoji: "🔇", label: "太吵了", value: "noisy" },
    { emoji: "🎒", label: "不够用", value: "limited" }
];

// 应用状态
const APP_STATE = {
    sessionId: null,
    selectedLocation: null,
    selectedEmotions: [],
    userInput: '',
    timePreference: null,
    activityPreference: null,
    currentDesign: null,
    language: localStorage.getItem('lang') || 'zh'
};

// 状态管理函数
function getState(key) {
    return APP_STATE[key];
}

function setState(key, value) {
    APP_STATE[key] = value;
    // 持久化重要状态到 localStorage
    if (key === 'sessionId' || key === 'language') {
        localStorage.setItem(key, value);
    }
}

function clearState() {
    APP_STATE.sessionId = null;
    APP_STATE.selectedLocation = null;
    APP_STATE.selectedEmotions = [];
    APP_STATE.userInput = '';
    APP_STATE.timePreference = null;
    APP_STATE.activityPreference = null;
    APP_STATE.currentDesign = null;
}

// 路由导航函数
function navigateTo(page) {
    if (PAGES[page]) {
        window.location.href = PAGES[page];
    } else {
        console.error('Unknown page:', page);
    }
}

// 导出给 HTML 页面使用
if (typeof window !== 'undefined') {
    window.API_BASE_URL = API_BASE_URL;
    window.API_KEY = API_KEY;
    window.PAGES = PAGES;
    window.EMOTION_TAGS = EMOTION_TAGS;
    window.APP_STATE = APP_STATE;
}

// 导出给其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        API_BASE_URL,
        API_KEY,
        PAGES,
        EMOTION_TAGS,
        APP_STATE,
        getState,
        setState,
        clearState,
        navigateTo
    };
}
