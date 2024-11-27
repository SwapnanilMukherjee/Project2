// frontend/src/types/document.ts
export interface Document {
    id: string;
    title: string;
    content: any;
    version: number;
    created_at: string;
    last_modified: string;
}

export interface DocumentMetadata {
    id: string;
    title: string;
    created_at: string;
    last_modified: string;
}

export interface DocumentChange {
    type: 'insert' | 'delete' | 'style' | 'line';
    position: number;
    content?: string;
    length?: number;
    attributes?: Record<string, any>;
    sourceVersion: number;
}

export interface DocumentVersion {
    version: number;
    timestamp: string;
    changes: DocumentChange[];
}

// frontend/src/types/formatting.ts
export interface StyleAttributes {
    bold?: boolean;
    italic?: boolean;
    underline?: boolean;
    fontSize?: number;
    color?: string;
    align?: 'left' | 'center' | 'right';
}

export interface StyleRange {
    pieceIndex: number;
    startOffset: number;
    length: number;
    attributes: StyleAttributes;
}

export interface LineMarker {
    pieceIndex: number;
    offset: number;
    type: 'paragraph' | 'bullet' | 'heading';
    properties: {
        indentation?: number;
        bulletType?: string;
        headingLevel?: number;
        alignment?: 'left' | 'center' | 'right';
    };
}

export interface BlockDescriptor {
    startPieceIndex: number;
    startOffset: number;
    endPieceIndex: number;
    endOffset: number;
    type: 'quote' | 'code' | 'list';
    properties: {
        style?: string;
        language?: string;
        listType?: string;
    };
}

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