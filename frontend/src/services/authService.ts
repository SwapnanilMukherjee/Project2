// frontend/src/services/authService.ts
interface AccessTokenResponse {
    token: string;
    expiresIn: number;
}

interface SessionResponse {
    session_id: string;
    expires_in: number;
}

export const authService = {
    // Get access token for document
    async getAccessToken(documentId: string, passkey: string): Promise<AccessTokenResponse> {
        const response = await api.post('/auth/token/', {
            document_id: documentId,
            passkey
        });
        return response.data;
    },

    // Verify access token
    async verifyToken(token: string): Promise<boolean> {
        try {
            await api.post('/auth/verify/', { token });
            return true;
        } catch {
            return false;
        }
    },

    // Create WebSocket session
    async createSession(documentId: string): Promise<SessionResponse> {
        const response = await api.post('/auth/session/', {
            document_id: documentId
        });
        return response.data;
    },

    // Set auth token for future requests
    setAuthToken(token: string): void {
        localStorage.setItem('auth_token', token);
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    },

    // Clear auth token
    clearAuthToken(): void {
        localStorage.removeItem('auth_token');
        delete api.defaults.headers.common['Authorization'];
    },

    // Store document passkey
    setDocumentPasskey(passkey: string): void {
        localStorage.setItem('document_passkey', passkey);
    },

    // Clear document passkey
    clearDocumentPasskey(): void {
        localStorage.removeItem('document_passkey');
    },

    // Check if user has access to document
    async checkAccess(documentId: string): Promise<boolean> {
        try {
            await api.get(`/documents/${documentId}/access/`);
            return true;
        } catch {
            return false;
        }
    }
};