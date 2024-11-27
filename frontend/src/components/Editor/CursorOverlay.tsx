// frontend/src/components/Editor/CursorOverlay.tsx
import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';

interface CursorPosition {
    userId: string;
    position: number;
    userName: string;
    color: string;
}

interface CursorOverlayProps {
    cursors: CursorPosition[];
    containerRef: React.RefObject<HTMLDivElement>;
}

interface CursorCoordinates {
    top: number;
    left: number;
}

export const CursorOverlay: React.FC<CursorOverlayProps> = ({
    cursors,
    containerRef,
}) => {
    const [coordinates, setCoordinates] = useState<Map<string, CursorCoordinates>>(new Map());

    useEffect(() => {
        if (!containerRef.current) return;

        // Calculate cursor positions
        const newCoordinates = new Map<string, CursorCoordinates>();

        cursors.forEach(cursor => {
            const coords = getCoordinatesFromPosition(cursor.position);
            if (coords) {
                newCoordinates.set(cursor.userId, coords);
            }
        });

        setCoordinates(newCoordinates);
    }, [cursors, containerRef]);

    const getCoordinatesFromPosition = (position: number): CursorCoordinates | null => {
        if (!containerRef.current) return null;

        const editorContent = containerRef.current;
        const range = document.createRange();
        const walker = document.createTreeWalker(
            editorContent,
            NodeFilter.SHOW_TEXT,
            null
        );

        let currentPos = 0;
        let node = walker.nextNode();

        // Find the text node and offset for cursor position
        while (node) {
            const nodeLength = node.textContent?.length || 0;
            if (currentPos + nodeLength >= position) {
                const offset = position - currentPos;
                range.setStart(node, offset);
                break;
            }
            currentPos += nodeLength;
            node = walker.nextNode();
        }

        if (!node) return null;

        // Get coordinates relative to editor container
        const rect = range.getBoundingClientRect();
        const containerRect = editorContent.getBoundingClientRect();

        return {
            top: rect.top - containerRect.top,
            left: rect.left - containerRect.left,
        };
    };

    return createPortal(
        <>
            {Array.from(coordinates.entries()).map(([userId, coords]) => {
                const cursor = cursors.find(c => c.userId === userId);
                if (!cursor) return null;

                return (
                    <div
                        key={userId}
                        className="absolute pointer-events-none"
                        style={{
                            transform: `translate(${coords.left}px, ${coords.top}px)`,
                        }}
                    >
                        {/* Cursor line */}
                        <div
                            className="w-0.5 h-5 absolute"
                            style={{ backgroundColor: cursor.color }}
                        />

                        {/* Username tooltip */}
                        <div
                            className="absolute left-2 top-0 px-2 py-1 text-xs text-white rounded whitespace-nowrap"
                            style={{ backgroundColor: cursor.color }}
                        >
                            {cursor.userName}
                        </div>
                    </div>
                );
            })}
        </>,
        containerRef.current || document.body
    );
};