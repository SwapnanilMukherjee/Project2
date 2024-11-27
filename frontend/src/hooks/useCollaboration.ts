// frontend/src/hooks/useCollaboration.ts
import { useState, useEffect, useCallback } from 'react';
import { uniqueId } from 'lodash';

interface CollaboratorInfo {
    id: string;
    name: string;
    color: string;
    cursorPosition: number;
    lastActive: Date;
}

export const useCollaboration = (documentId: string) => {
    const [collaborators, setCollaborators] = useState<Map<string, CollaboratorInfo>>(new Map());
    const [localUserId] = useState(() => uniqueId('user-'));

    const updateCollaborator = useCallback((userId: string, update: Partial<CollaboratorInfo>) => {
        setCollaborators(prev => {
            const next = new Map(prev);
            const current = next.get(userId) || {
                id: userId,
                name: 'Anonymous',
                color: getRandomColor(),
                cursorPosition: 0,
                lastActive: new Date()
            };
            next.set(userId, { ...current, ...update, lastActive: new Date() });
            return next;
        });
    }, []);

    const removeCollaborator = useCallback((userId: string) => {
        setCollaborators(prev => {
            const next = new Map(prev);
            next.delete(userId);
            return next;
        });
    }, []);

    // Clean up inactive collaborators
    useEffect(() => {
        const interval = setInterval(() => {
            const now = new Date();
            setCollaborators(prev => {
                const next = new Map(prev);
                for (const [id, info] of next) {
                    if (now.getTime() - info.lastActive.getTime() > 30000) { // 30 seconds timeout
                        next.delete(id);
                    }
                }
                return next;
            });
        }, 5000);

        return () => clearInterval(interval);
    }, []);

    return {
        localUserId,
        collaborators,
        updateCollaborator,
        removeCollaborator
    };
};

