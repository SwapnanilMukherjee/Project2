// frontend/src/services/websocketService.ts
interface WebSocketConfig {
    documentId: string;
    sessionId: string;
    onMessage: (message: any) => void;
    onClose: () => void;
}

export const websocketService = {
    connect({ documentId, sessionId, onMessage, onClose }: WebSocketConfig): WebSocket {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const ws = new WebSocket(
            `${protocol}//${window.location.host}/ws/document/${documentId}/?session=${sessionId}`
        );

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                onMessage(data);
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
            }
        };

        ws.onclose = () => {
            onClose();
        };

        return ws;
    },

    send(ws: WebSocket, message: any): void {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(message));
        }
    }
};