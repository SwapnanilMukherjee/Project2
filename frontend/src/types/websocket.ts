// frontend/src/types/websocket.ts
export type WebSocketMessage =
    | DocumentStateMessage
    | DocumentChangeMessage
    | CursorUpdateMessage
    | UserDisconnectedMessage
    | SyncRequestMessage
    | SyncResponseMessage;

export interface DocumentStateMessage {
    type: 'document_state';
    content: any;
    version: number;
    active_users: string[];
}

export interface DocumentChangeMessage {
    type: 'document_change';
    change: DocumentChange;
    user_id: string;
    new_version: number;
}

export interface CursorUpdateMessage {
    type: 'cursor_position';
    user_id: string;
    position: number;
    user_name: string;
    color: string;
}

export interface UserDisconnectedMessage {
    type: 'user_disconnected';
    user_id: string;
}

export interface SyncRequestMessage {
    type: 'sync_request';
    version: number;
}

export interface SyncResponseMessage {
    type: 'sync_response';
    content: any;
    version: number;
}

export interface WebSocketConfig {
    documentId: string;
    sessionId: string;
    onMessage: (message: WebSocketMessage) => void;
    onClose: () => void;
}