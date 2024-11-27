// frontend/src/components/Editor/EditorToolbar.tsx
import React from 'react';
import {
    Bold,
    Italic,
    Underline,
    List,
    FileDown,
    Clock,
    Type,
    AlignLeft,
    AlignCenter,
    AlignRight
} from 'lucide-react';
import {
    Tooltip,
    TooltipContent,
    TooltipTrigger,
} from '@/components/ui/tooltip';
import { Button } from '@/components/ui/button';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface EditorToolbarProps {
    onFormat: (format: string) => void;
    onDownload: (format: 'md' | 'docx') => void;
    onVersionHistory: () => void;
}

export const EditorToolbar: React.FC<EditorToolbarProps> = ({
    onFormat,
    onDownload,
    onVersionHistory,
}) => {
    return (
        <div className="flex items-center p-2 bg-gray-100 border-b gap-2">
            {/* Text Formatting */}
            <div className="flex items-center space-x-1 border-r pr-2">
                <Tooltip>
                    <TooltipTrigger asChild>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onFormat('bold')}
                            className="h-8 w-8 p-0"
                        >
                            <Bold className="h-4 w-4" />
                        </Button>
                    </TooltipTrigger>
                    <TooltipContent>Bold (Ctrl+B)</TooltipContent>
                </Tooltip>

                <Tooltip>
                    <TooltipTrigger asChild>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onFormat('italic')}
                            className="h-8 w-8 p-0"
                        >
                            <Italic className="h-4 w-4" />
                        </Button>
                    </TooltipTrigger>
                    <TooltipContent>Italic (Ctrl+I)</TooltipContent>
                </Tooltip>

                <Tooltip>
                    <TooltipTrigger asChild>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onFormat('underline')}
                            className="h-8 w-8 p-0"
                        >
                            <Underline className="h-4 w-4" />
                        </Button>
                    </TooltipTrigger>
                    <TooltipContent>Underline (Ctrl+U)</TooltipContent>
                </Tooltip>
            </div>

            {/* Font Size */}
            <div className="flex items-center space-x-1 border-r pr-2">
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm" className="h-8">
                            <Type className="h-4 w-4 mr-1" />
                            Font Size
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent>
                        {[12, 14, 16, 18, 20, 24, 28, 32].map(size => (
                            <DropdownMenuItem
                                key={size}
                                onClick={() => onFormat(`fontSize-${size}`)}
                            >
                                {size}px
                            </DropdownMenuItem>
                        ))}
                    </DropdownMenuContent>
                </DropdownMenu>
            </div>

            {/* Text Alignment */}
            <div className="flex items-center space-x-1 border-r pr-2">
                <Tooltip>
                    <TooltipTrigger asChild>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onFormat('align-left')}
                            className="h-8 w-8 p-0"
                        >
                            <AlignLeft className="h-4 w-4" />
                        </Button>
                    </TooltipTrigger>
                    <TooltipContent>Align Left</TooltipContent>
                </Tooltip>

                <Tooltip>
                    <TooltipTrigger asChild>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onFormat('align-center')}
                            className="h-8 w-8 p-0"
                        >
                            <AlignCenter className="h-4 w-4" />
                        </Button>
                    </TooltipTrigger>
                    <TooltipContent>Align Center</TooltipContent>
                </Tooltip>

                <Tooltip>
                    <TooltipTrigger asChild>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onFormat('align-right')}
                            className="h-8 w-8 p-0"
                        >
                            <AlignRight className="h-4 w-4" />
                        </Button>
                    </TooltipTrigger>
                    <TooltipContent>Align Right</TooltipContent>
                </Tooltip>
            </div>

            {/* Lists */}
            <div className="flex items-center space-x-1 border-r pr-2">
                <Tooltip>
                    <TooltipTrigger asChild>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onFormat('bullet')}
                            className="h-8 w-8 p-0"
                        >
                            <List className="h-4 w-4" />
                        </Button>
                    </TooltipTrigger>
                    <TooltipContent>Bullet List</TooltipContent>
                </Tooltip>
            </div>

            {/* Document Actions */}
            <div className="flex items-center space-x-1">
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm" className="h-8">
                            <FileDown className="h-4 w-4 mr-1" />
                            Download
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent>
                        <DropdownMenuItem onClick={() => onDownload('md')}>
                            Markdown (.md)
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => onDownload('docx')}>
                            Word (.docx)
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>

                <Button
                    variant="ghost"
                    size="sm"
                    onClick={onVersionHistory}
                    className="h-8"
                >
                    <Clock className="h-4 w-4 mr-1" />
                    History
                </Button>
            </div>
        </div>
    );
};