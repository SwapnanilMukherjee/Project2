// frontend/src/utils/diffing.ts
import { DocumentChange } from '../types/document';

export const generateDiff = (oldText: string, newText: string): DocumentChange[] => {
    const changes: DocumentChange[] = [];
    let i = 0;
    let j = 0;

    while (i < oldText.length || j < newText.length) {
        if (i < oldText.length && j < newText.length && oldText[i] === newText[j]) {
            i++;
            j++;
            continue;
        }

        // Find the next matching character
        let nextMatch = -1;
        let matchLength = 0;
        for (let k = 1; k < Math.max(oldText.length - i, newText.length - j); k++) {
            if (i + k < oldText.length && j + k < newText.length && oldText[i + k] === newText[j + k]) {
                nextMatch = k;
                matchLength = 1;
                while (i + k + matchLength < oldText.length &&
                    j + k + matchLength < newText.length &&
                    oldText[i + k + matchLength] === newText[j + k + matchLength]) {
                    matchLength++;
                }
                break;
            }
        }

        if (nextMatch === -1) {
            // No more matches found, handle remaining text
            if (i < oldText.length) {
                changes.push({
                    type: 'delete',
                    position: i,
                    length: oldText.length - i,
                    sourceVersion: 0, // Will be set by the caller
                });
            }
            if (j < newText.length) {
                changes.push({
                    type: 'insert',
                    position: j,
                    content: newText.slice(j),
                    sourceVersion: 0, // Will be set by the caller
                });
            }
            break;
        }

        // Handle changes before the next match
        if (i + nextMatch > i) {
            changes.push({
                type: 'delete',
                position: i,
                length: nextMatch,
                sourceVersion: 0,
            });
        }
        if (j + nextMatch > j) {
            changes.push({
                type: 'insert',
                position: j,
                content: newText.slice(j, j + nextMatch),
                sourceVersion: 0,
            });
        }

        i += nextMatch;
        j += nextMatch;
    }

    return optimizeChanges(changes);
};

const optimizeChanges = (changes: DocumentChange[]): DocumentChange[] => {
    const optimized: DocumentChange[] = [];
    let currentChange: DocumentChange | null = null;

    for (const change of changes) {
        if (!currentChange) {
            currentChange = { ...change };
            continue;
        }

        if (currentChange.type === change.type &&
            currentChange.position + (currentChange.length || currentChange.content?.length || 0) === change.position) {
            // Merge adjacent changes of the same type
            if (change.type === 'delete') {
                currentChange.length! += change.length!;
            } else if (change.type === 'insert') {
                currentChange.content! += change.content!;
            }
        } else {
            optimized.push(currentChange);
            currentChange = { ...change };
        }
    }

    if (currentChange) {
        optimized.push(currentChange);
    }

    return optimized;
};