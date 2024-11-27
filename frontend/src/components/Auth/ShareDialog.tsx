
// frontend/src/components/Auth/ShareDialog.tsx
import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Check, Copy, RefreshCw } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

interface ShareDialogProps {
    isOpen: boolean;
    onClose: () => void;
    documentId: string;
    onGenerateLink: () => Promise<string>;
}

export const ShareDialog: React.FC<ShareDialogProps> = ({
    isOpen,
    onClose,
    documentId,
    onGenerateLink
}) => {
    const [shareLink, setShareLink] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [copied, setCopied] = useState(false);
    const { toast } = useToast();

    const generateLink = async () => {
        setIsLoading(true);
        try {
            const link = await onGenerateLink();
            setShareLink(link);
        } catch (error) {
            toast({
                title: 'Error',
                description: 'Failed to generate share link',
                variant: 'destructive'
            });
        } finally {
            setIsLoading(false);
        }
    };

    const copyToClipboard = () => {
        navigator.clipboard.writeText(shareLink);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    React.useEffect(() => {
        if (isOpen && !shareLink) {
            generateLink();
        }
    }, [isOpen]);

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>Share Document</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                    <div className="flex items-center space-x-2">
                        <Input
                            value={shareLink}
                            readOnly
                            className="flex-1"
                            placeholder="Generating link..."
                        />
                        <Button
                            size="icon"
                            variant="outline"
                            onClick={copyToClipboard}
                            disabled={!shareLink}
                        >
                            {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                        </Button>
                    </div>
                    <Button
                        variant="outline"
                        onClick={generateLink}
                        disabled={isLoading}
                        className="w-full"
                    >
                        <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                        Generate New Link
                    </Button>
                    <p className="text-sm text-gray-500">
                        Anyone with this link and the document passkey can access this document.
                    </p>
                </div>
            </DialogContent>
        </Dialog>
    );
};