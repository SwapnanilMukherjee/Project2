//frontend / src / utils / errorHandling.ts
import { toast } from 'react-toastify';

interface APIError {
    error: string;
    detail?: string;
}

export const handleAPIError = (error: any) => {
    const errorData: APIError = error.response?.data || {
        error: 'An unexpected error occurred'
    };

    switch (error.response?.status) {
        case 401:
            toast.error('Authentication required. Please sign in again.');
            // Redirect to login or show auth modal
            break;

        case 403:
            toast.error('You do not have permission to perform this action.');
            break;

        case 404:
            toast.error('The requested resource was not found.');
            break;

        case 409:
            toast.error('Conflict detected. Please refresh and try again.');
            break;

        default:
            toast.error(errorData.detail || errorData.error);
    }

    return Promise.reject(error);
};

// Frontend error boundary component
import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
    children: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null
    };

    public static getDerivedStateFromError(error: Error): State {
        return {
            hasError: true,
            error
        };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('Uncaught error:', error, errorInfo);
    }

    public render() {
        if (this.state.hasError) {
            return (
                <div className= "min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8" >
                <div className="max-w-md w-full space-y-8" >
                    <div>
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900" >
                        Something went wrong
                            </h2>
                            < p className = "mt-2 text-center text-sm text-gray-600" >
                                { this.state.error?.message || 'An unexpected error occurred' }
                                </p>
                                </div>
                                < div className = "mt-5 flex justify-center" >
                                    <button
                onClick={ () => window.location.reload() }
            className = "inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                Refresh Page
                    </button>
                    </div>
                    </div>
                    </div>
      );
        }

        return this.props.children;
    }
}