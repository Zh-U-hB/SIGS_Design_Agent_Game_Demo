// api.js — 后端 API 客户端（完整实现）
// 职责：封装 fetch 请求，统一处理认证头、响应格式和错误

const API_CONFIG = {
    baseURL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8989'
        : window.location.origin,
    version: 'v1',
    get endpoints() {
        return {
            sessions: `${this.baseURL}/api/${this.version}/sessions`,
            designs: `${this.baseURL}/api/${this.version}/designs`,
            stats: `${this.baseURL}/api/${this.version}/stats`
        };
    }
};

const API = {
    async request(endpoint, options = {}) {
        const url = `${endpoint}`;

        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        // Add API Key if available (from backend config)
        const apiKey = localStorage.getItem('api_key');
        if (apiKey) {
            headers['X-API-Key'] = apiKey;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            const data = await response.json();

            if (data.code !== 0) {
                throw new Error(data.message || 'API request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    async createSession() {
        return this.request(API_CONFIG.endpoints.sessions, {
            method: 'POST'
        });
    },

    async submitDesign(data) {
        return this.request(API_CONFIG.endpoints.designs + '/input', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async confirmDesign(designId, data) {
        return this.request(`${API_CONFIG.endpoints.designs}/${designId}/confirm`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async getDesignStatus(designId) {
        return this.request(`${API_CONFIG.endpoints.designs}/${designId}/status`);
    },

    async getDesigns(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${API_CONFIG.endpoints.designs}?${queryString}` : API_CONFIG.endpoints.designs;
        return this.request(url);
    },

    async getMapData() {
        return this.request(`${API_CONFIG.endpoints.designs}/map`);
    },

    async getStats() {
        return this.request(API_CONFIG.endpoints.stats);
    },

    async likeDesign(designId) {
        const sessionId = getState('sessionId');
        return this.request(`${API_CONFIG.endpoints.designs}/${designId}/like?session_id=${encodeURIComponent(sessionId)}`, {
            method: 'POST'
        });
    },

    async unlikeDesign(designId) {
        const sessionId = getState('sessionId');
        return this.request(`${API_CONFIG.endpoints.designs}/${designId}/like?session_id=${encodeURIComponent(sessionId)}`, {
            method: 'DELETE'
        });
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { API, API_CONFIG };
}
