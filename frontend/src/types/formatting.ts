// frontend/src/types/formatting.ts
export interface StyleAttributes {
    bold?: boolean;
    italic?: boolean;
    underline?: boolean;
    fontSize?: number;
    color?: string;
    align?: 'left' | 'center' | 'right';
}

export interface StyleRange {
    pieceIndex: number;
    startOffset: number;
    length: number;
    attributes: StyleAttributes;
}

export interface LineMarker {
    pieceIndex: number;
    offset: number;
    type: 'paragraph' | 'bullet' | 'heading';
    properties: {
        indentation?: number;
        bulletType?: string;
        headingLevel?: number;
        alignment?: 'left' | 'center' | 'right';
    };
}

export interface BlockDescriptor {
    startPieceIndex: number;
    startOffset: number;
    endPieceIndex: number;
    endOffset: number;
    type: 'quote' | 'code' | 'list';
    properties: {
        style?: string;
        language?: string;
        listType?: string;
    };
}