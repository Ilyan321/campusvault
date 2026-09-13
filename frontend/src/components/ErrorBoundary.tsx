import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RotateCcw } from 'lucide-react';

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
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught React Error caught by ErrorBoundary:', error, errorInfo);
  }

  private handleReset = () => {
    try {
      localStorage.removeItem('campusvault_chat_sessions');
      localStorage.removeItem('campusvault_active_session_id');
    } catch {
      // ignore
    }
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#0B1118] text-[#E6EDF3] flex items-center justify-center p-6">
          <div className="max-w-md w-full p-6 rounded-lg border border-[#30363D] bg-[#161B22] shadow-2xl space-y-4 text-center">
            <div className="w-12 h-12 rounded-full bg-amber-500/10 text-amber-400 flex items-center justify-center mx-auto">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">Application State Reset Needed</h2>
              <p className="text-xs text-gray-400 mt-1.5 font-mono">
                {this.state.error?.message || 'A transient UI rendering issue occurred.'}
              </p>
            </div>
            <button
              onClick={this.handleReset}
              className="w-full py-2.5 px-4 rounded bg-amber-600 hover:bg-amber-500 text-white text-xs font-mono font-medium transition flex items-center justify-center gap-2"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset State & Reload App</span>
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
