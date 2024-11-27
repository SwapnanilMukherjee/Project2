// frontend/src/utils/formatting.ts
import { StyleAttributes, StyleRange, LineMarker } from '../types/formatting';

export const applyStyles = (text: string, styles: StyleRange[]): string => {
    let result = text;
    const sortedStyles = [...styles].sort((a, b) => b.startOffset - a.startOffset);

    sortedStyles.forEach(style => {
        const prefix = getStylePrefix(style.attributes);
        const suffix = getStyleSuffix(style.attributes);

        result =
            result.slice(0, style.startOffset) +
            prefix +
            result.slice(style.startOffset, style.startOffset + style.length) +
            suffix +
            result.slice(style.startOffset + style.length);
    });

    return result;
};

export const getStylePrefix = (attributes: StyleAttributes): string => {
    let prefix = '';
    if (attributes.bold) prefix += '<strong>';
    if (attributes.italic) prefix += '<em>';
    if (attributes.underline) prefix += '<u>';
    if (attributes.fontSize) prefix += `<span style="font-size: ${attributes.fontSize}px;">`;
    if (attributes.color) prefix += `<span style="color: ${attributes.color};">`;
    if (attributes.align) prefix += `<div style="text-align: ${attributes.align};">`;
    return prefix;
};

export const getStyleSuffix = (attributes: StyleAttributes): string => {
    let suffix = '';
    if (attributes.align) suffix = '</div>' + suffix;
    if (attributes.color) suffix = '</span>' + suffix;
    if (attributes.fontSize) suffix = '</span>' + suffix;
    if (attributes.underline) suffix = '</u>' + suffix;
    if (attributes.italic) suffix = '</em>' + suffix;
    if (attributes.bold) suffix = '</strong>' + suffix;
    return suffix;
};

export const applyLineFormatting = (text: string, lines: LineMarker[]): string => {
    const textLines = text.split('\n');
    const sortedLines = [...lines].sort((a, b) => a.offset - b.offset);

    sortedLines.forEach(line => {
        const lineNumber = text.slice(0, line.offset).split('\n').length - 1;
        if (lineNumber < textLines.length) {
            textLines[lineNumber] = formatLine(textLines[lineNumber], line);
        }
    });

    return textLines.join('\n');
};

export const formatLine = (text: string, marker: LineMarker): string => {
    const { type, properties } = marker;
    let formattedText = text;

    switch (type) {
        case 'bullet':
            const indent = '  '.repeat(properties.indentation || 0);
            formattedText = `${indent}• ${formattedText}`;
            break;
        case 'heading':
            formattedText = `${'#'.repeat(properties.headingLevel || 1)} ${formattedText}`;
            break;
    }

    if (properties.alignment) {
        formattedText = `<div style="text-align: ${properties.alignment}">${formattedText}</div>`;
    }

    return formattedText;
};