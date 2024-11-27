// frontend/src/store/store.ts
import { configureStore } from '@reduxjs/toolkit';
import documentReducer from './slices/documentSlice';
import userReducer from './slices/userSlice';

export const store = configureStore({
    reducer: {
        document: documentReducer,
        user: userReducer
    }
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;