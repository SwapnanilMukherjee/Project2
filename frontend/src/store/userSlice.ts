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