// frontend/src/App.tsx
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { Editor } from './components/Editor/Editor';
import { PasskeyModal } from './components/Auth/PasskeyModal';
import { RootState } from './store/store';
import { ErrorBoundary } from './utils/errorHandling';

const App: React.FC = () => {
    return (
        <ErrorBoundary>
            <Routes>
                {/* Redirect root to create new document */}
                <Route path="/" element={<Navigate to="/new" replace />} />

                {/* New document route */}
                <Route
                    path="/new"
                    element={
                        <RequirePasskey>
                            <Editor isNew />
                        </RequirePasskey>
                    }
                />

                {/* Existing document route */}
                <Route
                    path="/doc/:documentId"
                    element={
                        <RequirePasskey>
                            <Editor />
                        </RequirePasskey>
                    }
                />

                {/* Share link access route */}
                <Route
                    path="/share/:shareId"
                    element={
                        <RequirePasskey>
                            <Editor isShared />
                        </RequirePasskey>
                    }
                />

                {/* Fallback route */}
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </ErrorBoundary>
    );
};

// RequirePasskey component to handle authentication
interface RequirePasskeyProps {
    children: React.ReactNode;
}

const RequirePasskey: React.FC<RequirePasskeyProps> = ({ children }) => {
    const [showPasskeyModal, setShowPasskeyModal] = React.useState(false);
    const hasPasskey = useSelector((state: RootState) => !!state.user.id);

    React.useEffect(() => {
        if (!hasPasskey) {
            setShowPasskeyModal(true);
        }
    }, [hasPasskey]);

    const handlePasskeySubmit = async (passkey: string) => {
        try {
            // Handle passkey verification logic here
            setShowPasskeyModal(false);
        } catch (error) {
            console.error('Passkey verification failed:', error);
        }
    };

    if (!hasPasskey) {
        return (
            <PasskeyModal
                isOpen={showPasskeyModal}
                onClose={() => setShowPasskeyModal(false)}
                onSubmit={handlePasskeySubmit}
            />
        );
    }

    return <>{children}</>;
};

export default App;