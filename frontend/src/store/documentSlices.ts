// frontend/src/store/slices/documentSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface DocumentState {
    content: any;
    version: number;
    isLoading: boolean;
    error: string | null;
    isSaving: boolean;
    lastSaved: Date | null;
    currentSelection: {
        start: number;
        end: number;
    };
}

const initialState: DocumentState = {
    content: null,
    version: 1.0,
    isLoading: false,
    error: null,
    isSaving: false,
    lastSaved: null,
    currentSelection: {
        start: 0,
        end: 0
    }
};

const documentSlice = createSlice({
    name: 'document',
    initialState,
    reducers: {
        setContent: (state, action: PayloadAction<any>) => {
            state.content = action.payload;
        },
        setVersion: (state, action: PayloadAction<number>) => {
            state.version = action.payload;
        },
        setLoading: (state, action: PayloadAction<boolean>) => {
            state.isLoading = action.payload;
        },
        setError: (state, action: PayloadAction<string | null>) => {
            state.error = action.payload;
        },
        setSaving: (state, action: PayloadAction<boolean>) => {
            state.isSaving = action.payload;
        },
        setLastSaved: (state, action: PayloadAction<Date>) => {
            state.lastSaved = action.payload;
        },
        setSelection: (state, action: PayloadAction<{ start: number; end: number }>) => {
            state.currentSelection = action.payload;
        }
    }
});

export const {
    setContent,
    setVersion,
    setLoading,
    setError,
    setSaving,
    setLastSaved,
    setSelection
} = documentSlice.actions;

export default documentSlice.reducer;

// frontend/src/store/slices/userSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UserState {
    id: string | null;
    name: string;
    color: string;
    activeDocuments: string[];
}

const initialState: UserState = {
    id: null,
    name: 'Anonymous',
    color: '#' + Math.floor(Math.random() * 16777215).toString(16),
    activeDocuments: []
};

const userSlice = createSlice({
    name: 'user',
    initialState,
    reducers: {
        setUserId: (state, action: PayloadAction<string>) => {
            state.id = action.payload;
        },
        setUserName: (state, action: PayloadAction<string>) => {
            state.name = action.payload;
        },
        setUserColor: (state, action: PayloadAction<string>) => {
            state.color = action.payload;
        },
        addActiveDocument: (state, action: PayloadAction<string>) => {
            if (!state.activeDocuments.includes(action.payload)) {
                state.activeDocuments.push(action.payload);
            }
        },
        removeActiveDocument: (state, action: PayloadAction<string>) => {
            state.activeDocuments = state.activeDocuments.filter(id => id !== action.payload);
        }
    }
});

export const {
    setUserId,
    setUserName,
    setUserColor,
    addActiveDocument,
    removeActiveDocument
} = userSlice.actions;

export default userSlice.reducer;