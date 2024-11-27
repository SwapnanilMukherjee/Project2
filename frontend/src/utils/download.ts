// frontend/src/utils/download.ts
import { Document } from '../types/document';

export const downloadMarkdown = async (document: Document): Promise<void> => {
    try {
        const response = await fetch(`/api/documents/${document.id}/export/md`);
        if (!response.ok) throw new Error('Export failed');

        const blob = await response.blob();
        downloadBlob(blob, `${document.title}.md`);
    } catch (error) {
        console.error('Failed to download markdown:', error);
        throw error;
    }
};

export const downloadDocx = async (document: Document): Promise<void> => {
    try {
        const response = await fetch(`/api/documents/${document.id}/export/docx`);
        if (!response.ok) throw new Error('Export failed');

        const blob = await response.blob();
        downloadBlob(blob, `${document.title}.docx`);
    } catch (error) {
        console.error('Failed to download docx:', error);
        throw error;
    }
};

const downloadBlob = (blob: Blob, filename: string): void => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
};