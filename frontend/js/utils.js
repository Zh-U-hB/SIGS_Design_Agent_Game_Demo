// utils.js — DOM 和格式化工具函数（完整实现）
// 职责：提供选择器快捷方式、日期格式化、防抖、加载状态管理、Toast通知等通用工具

// DOM 选择器快捷方式
function $(selector) {
    return document.querySelector(selector);
}

function $$(selector) {
    return document.querySelectorAll(selector);
}

// 日期格式化
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString("zh-CN", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
    });
}

function formatRelativeTime(dateStr) {
    /** 格式化为相对时间（如：3分钟前） */
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return '刚刚';
    if (diffMins < 60) return `${diffMins}分钟前`;
    if (diffHours < 24) return `${diffHours}小时前`;
    if (diffDays < 7) return `${diffDays}天前`;
    return formatDate(dateStr);
}

// 防抖函数
function debounce(fn, delay = 300) {
    let timer;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}

// 节流函数
function throttle(fn, delay = 300) {
    let lastTime = 0;
    return function (...args) {
        const now = Date.now();
        if (now - lastTime >= delay) {
            lastTime = now;
            return fn.apply(this, args);
        }
    };
}

// 加载状态管理
function showLoading(container = document.body) {
    const overlay = document.createElement("div");
    overlay.className = "loading-overlay";
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(44, 42, 41, 0.4);
        backdrop-filter: blur(8px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
    `;
    overlay.innerHTML = `
        <div style="text-align: center;">
            <div style="
                width: 48px;
                height: 48px;
                border: 3px solid rgba(102, 8, 116, 0.2);
                border-top-color: #660874;
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
                margin: 0 auto 16px;
            "></div>
            <div style="color: white; font-size: 14px;">加载中...</div>
        </div>
        <style>
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
        </style>
    `;
    container.appendChild(overlay);
    return overlay;
}

function hideLoading(container = document.body) {
    const overlay = container.querySelector('.loading-overlay');
    if (overlay) {
        overlay.remove();
    }
}

// Toast 通知系统
const Toast = {
    container: null,

    init() {
        this.container = document.getElementById('toastContainer');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'toastContainer';
            this.container.className = 'toast-container';
            this.container.style.cssText = `
                position: fixed;
                top: 80px;
                right: 24px;
                z-index: 10000;
                display: flex;
                flex-direction: column;
                gap: 12px;
            `;
            document.body.appendChild(this.container);
        }
    },

    show(message, type = 'info', title = '', duration = 5000) {
        if (!this.container) this.init();

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        const colors = {
            success: '#10b981',
            error: '#ef4444',
            info: '#660874',
            warning: '#f59e0b'
        };

        const icons = {
            success: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="7" stroke="' + colors.success + '" stroke-width="1.5"/><path d="M7 10L9 12L13 8" stroke="' + colors.success + '" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
            error: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="7" stroke="' + colors.error + '" stroke-width="1.5"/><path d="M7 7L13 13M13 7L7 13" stroke="' + colors.error + '" stroke-width="1.5" stroke-linecap="round"/></svg>',
            info: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="7" stroke="' + colors.info + '" stroke-width="1.5"/><path d="M10 7V10M10 13V13.1" stroke="' + colors.info + '" stroke-width="1.5" stroke-linecap="round"/></svg>',
            warning: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M10 3L17 14H3L10 3Z" stroke="' + colors.warning + '" stroke-width="1.5" stroke-linejoin="round"/><path d="M10 8V11M10 13V13.1" stroke="' + colors.warning + '" stroke-width="1.5" stroke-linecap="round"/></svg>'
        };

        const titleText = title || (type === 'success' ? '成功' :
                                    type === 'error' ? '错误' :
                                    type === 'warning' ? '警告' : '提示');

        toast.style.cssText = `
            min-width: 280px;
            max-width: 380px;
            padding: 16px 20px;
            background: #ffffff;
            border-radius: 10px;
            box-shadow: 0 8px 32px rgba(102, 8, 116, 0.15);
            border-left: 4px solid ${colors[type]};
            display: flex;
            align-items: flex-start;
            gap: 12px;
            animation: toastIn 0.3s ease;
        `;

        toast.innerHTML = `
            ${icons[type]}
            <div class="toast-content">
                <div class="toast-title" style="font-size: 14px; font-weight: 600; color: #2c2a29; margin-bottom: 4px;">${titleText}</div>
                <div class="toast-message" style="font-size: 13px; color: #6b6560; line-height: 1.4;">${message}</div>
            </div>
            <style>
                @keyframes toastIn {
                    from {
                        opacity: 0;
                        transform: translateX(100%);
                    }
                    to {
                        opacity: 1;
                        transform: translateX(0);
                    }
                }
            </style>
        `;

        this.container.appendChild(toast);

        // Auto remove after duration
        setTimeout(() => {
            this.remove(toast);
        }, duration);

        return toast;
    },

    success(message, title = '') {
        return this.show(message, 'success', title);
    },

    error(message, title = '') {
        return this.show(message, 'error', title);
    },

    info(message, title = '') {
        return this.show(message, 'info', title);
    },

    warning(message, title = '') {
        return this.show(message, 'warning', title);
    },

    remove(toast) {
        if (toast && toast.parentNode) {
            toast.style.animation = 'toastOut 0.3s ease forwards';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }
    }
};

// 添加样式到页面
function injectStyles() {
    if (document.getElementById('utils-injected-styles')) return;

    const style = document.createElement('style');
    style.id = 'utils-injected-styles';
    style.textContent = `
        @keyframes toastOut {
            to {
                opacity: 0;
                transform: translateX(100%);
            }
        }
    `;
    document.head.appendChild(style);
}

// 初始化样式
injectStyles();

// 导出给 HTML 页面使用
if (typeof window !== 'undefined') {
    window.$ = $;
    window.$$ = $$;
    window.formatDate = formatDate;
    window.formatRelativeTime = formatRelativeTime;
    window.debounce = debounce;
    window.throttle = throttle;
    window.showLoading = showLoading;
    window.hideLoading = hideLoading;
    window.Toast = Toast;
}

// 导出给其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        $, $$,
        formatDate,
        formatRelativeTime,
        debounce,
        throttle,
        showLoading,
        hideLoading,
        Toast
    };
}
