// frontend/src/hooks/useAutoSave.ts
import { useEffect, useRef } from 'react';

interface AutoSaveOptions {
    documentId: string;
    content: any;
    version: number;
    interval?: number;
    onSaving?: () => void;
    onSaved?: () => void;
    onError?: (error: Error) => void;
}

export const useAutoSave = ({
    documentId,
    content,
    version,
    interval = 30000,
    onSaving,
    onSaved,
    onError
}: AutoSaveOptions) => {
    const lastSavedRef = useRef<number>(version);
    const saveTimeoutRef = useRef<NodeJS.Timeout>();

    const save = async () => {
        if (version === lastSavedRef.current) return;

        try {
            onSaving?.();

            const response = await fetch(`/api/documents/${documentId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    content,
                    version
                })
            });

            if (!response.ok) {
                throw new Error('Failed to save document');
            }

            lastSavedRef.current = version;
            onSaved?.();
        } catch (error) {
            onError?.(error as Error);
        }
    };

    useEffect(() => {
        if (saveTimeoutRef.current) {
            clearTimeout(saveTimeoutRef.current);
        }

        saveTimeoutRef.current = setTimeout(save, interval);

        return () => {
            if (saveTimeoutRef.current) {
                clearTimeout(saveTimeoutRef.current);
            }
        };
    }, [content, version, interval]);

    return {
        save,
        lastSavedVersion: lastSavedRef.current
    };
};

// Helper function for random colors
const getRandomColor = () => {
    const colors = [
        '#FF6B6B', // Red
        '#4ECDC4', // Teal
        '#45B7D1', // Blue
        '#96CEB4', // Green
        '#FFEEAD', // Yellow
        '#D4A5A5', // Pink
        '#9B59B6', // Purple
        '#3498DB'  // Light Blue
    ];
    return colors[Math.floor(Math.random() * colors.length)];
};