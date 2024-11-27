// frontend/src/utils/validation.ts
export const validatePasskey = (passkey: string): boolean => {
    // Passkey must be at least 6 characters long
    return passkey.length >= 6;
};

export const validateDocumentTitle = (title: string): boolean => {
    // Title must be between 1 and 100 characters
    return title.length > 0 && title.length <= 100;
};