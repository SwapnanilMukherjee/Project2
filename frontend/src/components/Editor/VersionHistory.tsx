// frontend/src/components/Editor/VersionHistory.tsx
import React, { useEffect, useState } from 'react';
import {
    Sheet,
    SheetContent,
    SheetHeader,
    SheetTitle,
} from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { formatDistanceToNow } from 'date-fns';

interface Version {
    version: number;
    timestamp: string;
    userId: string;
    userName: string;
    changes: Array<{
        type: string;
        content?: string;
        position: number;
        length?: number;
        attributes?: Record<string, any>;
    }>;
}

interface VersionHistoryProps {
    documentId: string;
    onClose: () => void;
    onRestore: (version: number) => void;
}

export const VersionHistory: React.FC<VersionHistoryProps> = ({
    documentId,
    onClose,
    onRestore,
}) => {
    const [versions, setVersions] = useState<Version[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchVersionHistory();
    }, [documentId]);

    const fetchVersionHistory = async () => {
        try {
            const response = await fetch(`/api/documents/${documentId}/versions`);
            if (!response.ok) throw new Error('Failed to fetch version history');

            const data = await response.json();
            setVersions(data);
            setLoading(false);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
            setLoading(false);
        }
    };

    const handleRestore = async (version: number) => {
        const confirmed = window.confirm(
            'Are you sure you want to restore this version? This will overwrite the current version.'
        );

        if (confirmed) {
            onRestore(version);
            onClose();
        }
    };

    const getChangeDescription = (change: Version['changes'][0]): string => {
        switch (change.type) {
            case 'insert':
                return `Inserted "${change.content?.slice(0, 20)}${change.content && change.content.length > 20 ? '...' : ''}"`;
            case 'delete':
                return `Deleted ${change.length} characters`;
            case 'style':
                return `Applied ${Object.keys(change.attributes || {}).join(', ')} formatting`;
            default:
                return 'Made changes';
        }
    };

    return (
        <Sheet open onOpenChange={onClose}>
            <SheetContent side="right" className="w-96">
                <SheetHeader>
                    <SheetTitle>Version History</SheetTitle>
                </SheetHeader>

                {loading ? (
                    <div className="flex items-center justify-center h-full">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900" />
                    </div>
                ) : error ? (
                    <div className="p-4 text-red-500">
                        {error}
                    </div>
                ) : (
                    <ScrollArea className="h-full pr-4">
                        <div className="space-y-4 py-4">
                            {versions.map((version, index) => (
                                <div
                                    key={version.version}
                                    className="border rounded-lg p-4 space-y-2"
                                >
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <div className="font-medium">
                                                {formatDistanceToNow(new Date(version.timestamp))} ago
                                            </div>
                                            <div className="text-sm text-gray-500">
                                                by {version.userName}
                                            </div>
                                        </div>
                                        {index > 0 && (
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => handleRestore(version.version)}
                                            >
                                                Restore
                                            </Button>
                                        )}
                                    </div>

                                    <div className="text-sm space-y-1">
                                        {version.changes.map((change, i) => (
                                            <div key={i} className="text-gray-600">
                                                • {getChangeDescription(change)}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </ScrollArea>
                )}
            </SheetContent>
        </Sheet>
    );
};