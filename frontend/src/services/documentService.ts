// frontend/src/services/documentService.ts
export interface CreateDocumentParams {
    title: string;
    passkey: string;
}

export interface DocumentResponse {
    id: string;
    title: string;
    content: any;
    version: number;
    created_at: string;
    last_modified: string;
}

export interface DocumentChange {
    type: 'insert' | 'delete' | 'style' | 'line';
    position: number;
    content?: string;
    length?: number;
    attributes?: Record<string, any>;
}

export const documentService = {
    // Create new document
    async createDocument(params: CreateDocumentParams): Promise<DocumentResponse> {
        const response = await api.post('/documents/create/', params);
        return response.data;
    },

    // Get document by ID
    async getDocument(documentId: string): Promise<DocumentResponse> {
        const response = await api.get(`/documents/${documentId}/`);
        return response.data;
    },

    // Update document content
    async updateDocument(documentId: string, changes: DocumentChange[]): Promise<void> {
        await api.put(`/documents/${documentId}/`, { changes });
    },

    // Get version history
    async getVersionHistory(documentId: string): Promise<any[]> {
        const response = await api.get(`/documents/${documentId}/versions/`);
        return response.data.versions;
    },

    // Restore version
    async restoreVersion(documentId: string, version: number): Promise<void> {
        await api.post(`/documents/${documentId}/versions/`, { version });
    },

    // Export document
    async exportDocument(documentId: string, format: 'md' | 'docx'): Promise<Blob> {
        const response = await api.get(
            `/documents/${documentId}/export/${format}/`,
            { responseType: 'blob' }
        );
        return response.data;
    },

    // Create share link
    async createShareLink(documentId: string): Promise<string> {
        const response = await api.post(`/documents/${documentId}/share/`);
        return response.data.share_url;
    },

    // Access shared document
    async accessSharedDocument(shareId: string, passkey: string): Promise<string> {
        const response = await api.post(`/documents/access/${shareId}/`, { passkey });
        return response.data.redirect_url;
    },

    // Get active users
    async getActiveUsers(documentId: string): Promise<string[]> {
        const response = await api.get(`/documents/${documentId}/users/`);
        return response.data.users;
    }
};