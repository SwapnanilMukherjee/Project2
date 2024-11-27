// frontend/src/components/Auth/PasskeyModal.tsx
import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';

interface PasskeyModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (passkey: string) => Promise<void>;
    title?: string;
}

export const PasskeyModal: React.FC<PasskeyModalProps> = ({
    isOpen,
    onClose,
    onSubmit,
    title = 'Enter Document Passkey'
}) => {
    const [passkey, setPasskey] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { toast } = useToast();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!passkey.trim()) {
            toast({
                title: 'Error',
                description: 'Please enter a passkey',
                variant: 'destructive'
            });
            return;
        }

        setIsLoading(true);
        try {
            await onSubmit(passkey);
            onClose();
        } catch (error) {
            toast({
                title: 'Error',
                description: 'Invalid passkey',
                variant: 'destructive'
            });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>{title}</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <Input
                        type="password"
                        placeholder="Enter passkey"
                        value={passkey}
                        onChange={(e) => setPasskey(e.target.value)}
                        autoFocus
                    />
                    <div className="flex justify-end space-x-2">
                        <Button variant="outline" onClick={onClose} disabled={isLoading}>
                            Cancel
                        </Button>
                        <Button type="submit" disabled={isLoading}>
                            {isLoading ? 'Verifying...' : 'Submit'}
                        </Button>
                    </div>
                </form>
            </DialogContent>
        </Dialog>
    );
};