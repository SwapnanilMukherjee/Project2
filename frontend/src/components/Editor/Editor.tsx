// frontend/src/components/Editor/Editor.tsx
import React, { useEffect, useRef, useState } from 'react';
import { useWebSocket } from '../../hooks/useWebSocket';
import { useDocument } from '../../hooks/useDocument';
import { EditorToolbar } from './EditorToolbar';
import { CursorOverlay } from './CursorOverlay.tsx';
import { VersionHistory } from './VersionHistory';
import { debounce } from 'lodash';

interface EditorProps {
    documentId: string;
    passkey: string;
}

interface Selection {
    start: number;
    end: number;
}

interface CursorPosition {
    userId: string;
    position: number;
    userName: string;
    color: string;
}

export const Editor: React.FC<EditorProps> = ({ documentId, passkey }) => {
    const editorRef = useRef<HTMLDivElement>(null);
    const [selection, setSelection] = useState<Selection>({ start: 0, end: 0 });
    const [cursors, setCursors] = useState<CursorPosition[]>([]);
    const [isReady, setIsReady] = useState(false);
    const [showVersionHistory, setShowVersionHistory] = useState(false);

    const { document, version, applyChange, setDocument } = useDocument(documentId);
    const { socket, connectionStatus } = useWebSocket({
        documentId,
        passkey,
        onMessage: handleWebSocketMessage,
    });

    // Handle incoming WebSocket messages
    function handleWebSocketMessage(message: any) {
        const data = JSON.parse(message);

        switch (data.type) {
            case 'document_state':
                setDocument(data.content);
                setIsReady(true);
                break;
            case 'document_change':
                if (data.userId !== socket?.id) {
                    applyChange(data.change);
                }
                break;
            case 'cursor_position':
                updateCursor(data.userId, data.position, data.userName, data.color);
                break;
            case 'user_disconnected':
                removeCursor(data.userId);
                break;
        }
    }

    // Update cursor positions
    const updateCursor = (userId: string, position: number, userName: string, color: string) => {
        setCursors(prev => {
            const existing = prev.findIndex(c => c.userId === userId);
            if (existing >= 0) {
                const updated = [...prev];
                updated[existing] = { userId, position, userName, color };
                return updated;
            }
            return [...prev, { userId, position, userName, color }];
        });
    };

    // Remove cursor when user disconnects
    const removeCursor = (userId: string) => {
        setCursors(prev => prev.filter(c => c.userId !== userId));
    };

    // Handle local text changes
    const handleTextChange = debounce((event: React.FormEvent<HTMLDivElement>) => {
        const content = event.currentTarget.innerText;
        const change = {
            type: 'text',
            operation: {
                type: 'insert',
                position: selection.start,
                content: content,
            },
            sourceVersion: version,
        };

        socket?.send(JSON.stringify({
            type: 'operation',
            change,
        }));

        applyChange(change);
    }, 100);

    // Handle selection changes
    const handleSelectionChange = () => {
        const sel = window.getSelection();
        if (!sel || !editorRef.current) return;

        const range = sel.getRangeAt(0);
        const start = getTextPosition(editorRef.current, range.startContainer, range.startOffset);
        const end = getTextPosition(editorRef.current, range.endContainer, range.endOffset);

        setSelection({ start, end });

        // Send cursor position to other users
        socket?.send(JSON.stringify({
            type: 'cursor_update',
            position: start,
        }));
    };

    // Calculate text position relative to editor root
    const getTextPosition = (root: Node, node: Node, offset: number): number => {
        let position = 0;
        const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);

        while (walker.nextNode()) {
            const current = walker.currentNode;
            if (current === node) {
                return position + offset;
            }
            position += current.textContent?.length || 0;
        }
        return position;
    };

    // Handle formatting
    const applyFormat = (format: string) => {
        if (selection.start === selection.end) return;

        const change = {
            type: 'style',
            operation: {
                type: 'style',
                position: selection.start,
                length: selection.end - selection.start,
                attributes: { [format]: true },
            },
            sourceVersion: version,
        };

        socket?.send(JSON.stringify({
            type: 'operation',
            change,
        }));

        applyChange(change);
    };

    // Download document
    const handleDownload = async (format: 'md' | 'docx') => {
        try {
            const response = await fetch(`/api/documents/${documentId}/download?format=${format}`);
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `document.${format}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Download failed:', error);
        }
    };

    return (
        <div className="flex flex-col h-screen">
            <EditorToolbar
                onFormat={applyFormat}
                onDownload={handleDownload}
                onVersionHistory={() => setShowVersionHistory(true)}
            />

            <div className="relative flex-grow overflow-auto bg-white">
                <div
                    ref={editorRef}
                    className="p-4 min-h-full prose prose-sm sm:prose lg:prose-lg"
                    contentEditable={isReady}
                    onInput={handleTextChange}
                    onSelect={handleSelectionChange}
                    suppressContentEditableWarning
                />

                <CursorOverlay
                    cursors={cursors}
                    containerRef={editorRef}
                />
            </div>

            {showVersionHistory && (
                <VersionHistory
                    documentId={documentId}
                    onClose={() => setShowVersionHistory(false)}
                    onRestore={(version) => {
                        socket?.send(JSON.stringify({
                            type: 'restore_version',
                            version,
                        }));
                    }}
                />
            )}
        </div>
    );
};