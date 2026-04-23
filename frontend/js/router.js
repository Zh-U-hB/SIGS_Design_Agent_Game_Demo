// router.js — 页面导航管理（完整实现）
// 职责：提供页面跳转功能，自动计算 pages 目录的基础路径，支持参数传递和历史管理

function navigateTo(pageName, params = {}) {
    /** 跳转到指定页面，支持参数传递 */
    const baseUrl = getPagesBasePath();
    const url = new URL(`${baseUrl}${pageName}`, window.location.origin);

    // 添加查询参数
    Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
            url.searchParams.set(key, value);
        }
    });

    window.location.href = url.toString();
}

function getPagesBasePath() {
    /** 获取 pages 目录的基础路径 */
    const currentPath = window.location.pathname;
    if (currentPath.includes("/pages/")) {
        return currentPath.substring(0, currentPath.indexOf("/pages/") + "/pages/".length);
    }
    // 如果在根目录或其他位置，返回相对路径
    if (currentPath.endsWith('/') || currentPath === '') {
        return 'pages/';
    }
    return './pages/';
}

function getCurrentPage() {
    /** 获取当前页面名称 */
    const path = window.location.pathname;
    const match = path.match(/\/([^\/]+)\.html$/);
    return match ? match[1] + '.html' : null;
}

function goBack() {
    /** 返回上一页 */
    window.history.back();
}

function replaceWith(pageName, params = {}) {
    /** 替换当前页面（不产生历史记录） */
    const baseUrl = getPagesBasePath();
    const url = new URL(`${baseUrl}${pageName}`, window.location.origin);

    Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
            url.searchParams.set(key, value);
        }
    });

    window.location.replace(url.toString());
}

function reload() {
    /** 重新加载当前页面 */
    window.location.reload();
}

// URL 参数工具
function getUrlParams() {
    /** 获取当前页面的 URL 参数 */
    const params = {};
    const searchParams = new URLSearchParams(window.location.search);
    searchParams.forEach((value, key) => {
        params[key] = value;
    });
    return params;
}

function getUrlParam(key) {
    /** 获取指定 URL 参数 */
    const params = new URLSearchParams(window.location.search);
    return params.get(key);
}

function setUrlParam(key, value) {
    /** 设置 URL 参数（不刷新页面） */
    const url = new URL(window.location);
    url.searchParams.set(key, value);
    window.history.replaceState({}, '', url.toString());
}

// 页面加载状态管理
function onPageLoad(callback) {
    /** 页面加载完成后执行回调 */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', callback);
    } else {
        callback();
    }
}

// 页面可见性变化监听
function onVisibilityChange(callback) {
    /** 监听页面可见性变化 */
    document.addEventListener('visibilitychange', () => {
        callback(!document.hidden);
    });
}

// 页面离开前确认
function onBeforeLeave(message) {
    /** 页面离开前确认 */
    window.addEventListener('beforeunload', (e) => {
        e.preventDefault();
        e.returnValue = message;
        return message;
    });
}

// 滚动到页面顶部
function scrollToTop(smooth = true) {
    window.scrollTo({
        top: 0,
        behavior: smooth ? 'smooth' : 'auto'
    });
}

// 滚动到指定元素
function scrollToElement(selector, options = {}) {
    const element = document.querySelector(selector);
    if (element) {
        element.scrollIntoView({
            behavior: options.smooth !== false ? 'smooth' : 'auto',
            block: options.block || 'start',
            inline: options.inline || 'nearest'
        });
    }
}

// 导出给 HTML 页面使用
if (typeof window !== 'undefined') {
    window.navigateTo = navigateTo;
    window.getPagesBasePath = getPagesBasePath;
    window.getCurrentPage = getCurrentPage;
    window.goBack = goBack;
    window.replaceWith = replaceWith;
    window.reload = reload;
    window.getUrlParams = getUrlParams;
    window.getUrlParam = getUrlParam;
    window.setUrlParam = setUrlParam;
    window.onPageLoad = onPageLoad;
    window.onVisibilityChange = onVisibilityChange;
    window.onBeforeLeave = onBeforeLeave;
    window.scrollToTop = scrollToTop;
    window.scrollToElement = scrollToElement;
}

// 导出给其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        navigateTo,
        getPagesBasePath,
        getCurrentPage,
        goBack,
        replaceWith,
        reload,
        getUrlParams,
        getUrlParam,
        setUrlParam,
        onPageLoad,
        onVisibilityChange,
        onBeforeLeave,
        scrollToTop,
        scrollToElement
    };
}
