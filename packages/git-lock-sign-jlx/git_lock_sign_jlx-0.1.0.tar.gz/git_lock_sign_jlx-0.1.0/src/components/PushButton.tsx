/**
 * Push button component for pushing changes to remote GitLab repository.
 */

import React, { useState, useEffect } from 'react';
import { showDialog, Dialog } from '@jupyterlab/apputils';
import { NotebookPanel } from '@jupyterlab/notebook';

import { gitLockSignAPI, getAbsoluteNotebookPathSync } from '../services/api';
import {
  IPushButtonState,
  INotebookLockManager
} from '../types';

/**
 * Props for the push button component.
 */
export interface IPushButtonProps {
  notebookPanel: NotebookPanel;
  onStateChange?: (state: IPushButtonState) => void;
  lockManager?: INotebookLockManager;
}

/**
 * React component for the push button.
 */
export const PushButtonComponent: React.FC<IPushButtonProps> = ({
  notebookPanel,
  onStateChange,
  lockManager
}) => {
  const [state, setState] = useState<IPushButtonState>({
    loading: false,
    error: null,
    lastPushTime: undefined,
    shouldRender: true // Default to visible until config is loaded
  });

  // Load button configuration on component mount
  useEffect(() => {
    const loadButtonConfig = async () => {
      try {
        const config = await gitLockSignAPI.getConfig();
        setState(prev => ({
          ...prev,
          shouldRender: config.enable_push_button ?? true
        }));
      } catch (error) {
        console.error('❌ Failed to load button configuration:', error);
        // Keep default visible state on error
      }
    };

    loadButtonConfig();
  }, []);

  // Update parent component when state changes
  useEffect(() => {
    if (onStateChange) {
      onStateChange(state);
    }
  }, [state, onStateChange]);

  /**
   * Handle push button click.
   */
  const handlePushClick = async (): Promise<void> => {
    if (state.loading || !notebookPanel?.content?.model) {
      return;
    }

    const result = await showDialog({
      title: 'Push to Remote Repository',
      body: 'This will push your committed changes to the remote git server. Make sure you have committed your changes first.',
      buttons: [Dialog.cancelButton(), Dialog.okButton({ label: 'Push' })]
    });

    if (!result.button.accept) {
      return;
    }

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const notebookPath = getAbsoluteNotebookPathSync(notebookPanel.context.path);

      console.log('🚀 Starting push operation');

      // Push to the repository (provisioning was handled at session startup)
      const pushResponse = await gitLockSignAPI.pushToRepository(notebookPath);

      if (pushResponse.success) {
        console.log('✅ Push operation completed successfully');
        setState(prev => ({
          ...prev,
          loading: false,
          success: true,
          error: null
        }));
        
        setTimeout(() => {
          setState(prev => ({ ...prev, success: false }));
        }, 3000);
      } else {
        console.error('❌ Push operation failed:', pushResponse.error);
        setState(prev => ({
          ...prev,
          error: pushResponse.error || 'Push failed',
          loading: false
        }));
      }
    } catch (error) {
      console.error('❌ Push operation error:', error);
      setState(prev => ({
        ...prev,
        error: `Push failed: ${error}`,
        loading: false
      }));
    }
  };

  /**
   * Get button title tooltip text.
   */
  const getButtonTitle = (): string => {
    if (state.loading) {
      return 'Pushing changes to remote repository...';
    }
    if (state.error) {
      return `Push error: ${state.error}`;
    }
    if (state.lastPushTime) {
      return `Last pushed: ${state.lastPushTime}`;
    }
    return 'Push committed changes to remote GitLab repository';
  };

  /**
   * Get button icon class.
   */
  const getButtonIcon = (): string => {
    if (state.loading) {
      return 'jp-CircularProgressIcon';
    }
    return 'jp-GitPushIcon';
  };

  /**
   * Get button text.
   */
  const getButtonText = (): string => {
    if (state.loading) {
      return 'Pushing...';
    }
    return 'Push';
  };

  // Don't render the button if disabled by configuration
  if (!state.shouldRender) {
    return null;
  }

  return (
    <button
      className={`git-lock-sign-button push ${state.loading ? 'loading' : ''}`}
      onClick={handlePushClick}
      disabled={state.loading}
      title={getButtonTitle()}
    >
      <span className={`jp-Icon ${getButtonIcon()}`} />
      <span className="button-text">{getButtonText()}</span>
      {state.error && (
        <span className="error-indicator" title={state.error}>
          ⚠️
        </span>
      )}
    </button>
  );
};

/**
 * Push button widget for notebook toolbar.
 */
export class PushButtonWidget extends React.Component<IPushButtonProps> {
  render() {
    return <PushButtonComponent {...this.props} />;
  }
}
