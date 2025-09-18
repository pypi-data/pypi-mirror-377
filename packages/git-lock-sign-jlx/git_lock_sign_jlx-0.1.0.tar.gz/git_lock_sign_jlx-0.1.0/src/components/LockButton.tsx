/**
 * Lock button component for notebook toolbar.
 */

import React, { useState, useEffect } from 'react';

import { ReactWidget } from '@jupyterlab/apputils';
import { NotebookPanel } from '@jupyterlab/notebook';
import { showErrorMessage, showDialog, Dialog } from '@jupyterlab/apputils';

import { gitLockSignAPI, getAbsoluteNotebookPathSync, stripRTCPrefix } from '../services/api';
import {
  ILockButtonState
} from '../types';
import { NotebookLockManager } from './NotebookLockManager';

/**
 * State for the lock button dialog.
 */
interface ILockDialogState {
  showDialog: boolean;
  commitMessage: string;
  isProcessing: boolean;
}

/**
 * Props for the LockButton component.
 */
interface ILockButtonProps {
  notebookPanel: NotebookPanel;
  onStateChange?: (state: ILockButtonState) => void;
  lockManager?: NotebookLockManager;
}


/**
 * React component for the lock/unlock button.
 */
const LockButtonComponent: React.FC<ILockButtonProps> = ({
  notebookPanel,
  onStateChange,
  lockManager
}) => {
  const [state, setState] = useState<ILockButtonState>({
    locked: false,
    loading: false,
    error: null,
    signatureInfo: null,
    shouldRender: true // Default to visible until config is loaded
  });

  const [dialogState, setDialogState] = useState<ILockDialogState>({
    showDialog: false,
    commitMessage: '',
    isProcessing: false
  });


  // Update parent component when state changes
  useEffect(() => {
    if (onStateChange) {
      onStateChange(state);
    }
  }, [state, onStateChange]);

  // Load button configuration on component mount
  useEffect(() => {
    const loadButtonConfig = async () => {
      try {
        const config = await gitLockSignAPI.getConfig();
        setState(prev => ({
          ...prev,
          shouldRender: config.enable_lock_button ?? true
        }));
      } catch (error) {
        console.error('❌ Failed to load button configuration:', error);
        // Keep default visible state on error
      }
    };

    loadButtonConfig();
  }, []);

  // Check initial status when component mounts
  useEffect(() => {
    checkNotebookStatus();
  }, [notebookPanel]);

  /**
   * Check the current lock status of the notebook.
   */
  const checkNotebookStatus = async (): Promise<void> => {
    if (!notebookPanel?.content?.model) {
      return;
    }

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const notebookPath = getAbsoluteNotebookPathSync(notebookPanel.context.path);
      const notebookContent = notebookPanel.content.model?.toJSON();
      if (!notebookContent) {
        setState(prev => ({
          ...prev,
          error: 'Could not get notebook content',
          loading: false
        }));
        return;
      }
      const response = await gitLockSignAPI.checkNotebookStatus(notebookContent, notebookPath);

      if (response.success) {
        setState(prev => ({
          ...prev,
          locked: response.locked || false,
          signatureInfo: response.metadata || null,
          loading: false
        }));
      } else {
        setState(prev => ({
          ...prev,
          error: response.error || 'Failed to check notebook status',
          loading: false
        }));
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: `Error checking status: ${error}`,
        loading: false
      }));
    }
  };

  /**
   * Handle lock button click.
   */
  const handleLockClick = (): void => {
    if (state.loading || !notebookPanel?.content?.model) {
      return;
    }

    if (state.locked) {
      // For unlock, show confirmation dialog
      handleUnlockClick();
    } else {
      // For lock, show commit dialog
      const notebookName = stripRTCPrefix(notebookPanel.context.path).split('/').pop() || 'notebook';
      const timestamp = new Date().toLocaleString();
      const defaultMessage = `Lock and sign ${notebookName} - ${timestamp}`;

      setDialogState({
        showDialog: true,
        commitMessage: defaultMessage,
        isProcessing: false
      });
    }
  };

  /**
   * Handle unlock button click.
   */
  const handleUnlockClick = async (): Promise<void> => {
    const result = await showDialog({
      title: 'Unlock Notebook',
      body: 'Are you sure you want to unlock this notebook? This will verify the signature and remove the lock.',
      buttons: [Dialog.cancelButton(), Dialog.okButton({ label: 'Unlock' })]
    });

    if (!result.button.accept) {
      return;
    }

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const notebookPath = getAbsoluteNotebookPathSync(notebookPanel.context.path);
      const notebookContent = notebookPanel.content.model?.toJSON();
      if (!notebookContent) {
        setState(prev => ({
          ...prev,
          error: 'Could not get notebook content',
          loading: false
        }));
        showErrorMessage('Lock/Unlock Error', 'Could not get notebook content');
        return;
      }

      const unlockResponse = await gitLockSignAPI.unlockNotebook(notebookPath, notebookContent);

      if (unlockResponse.success && unlockResponse.metadata) {
        setState(prev => ({
          ...prev,
          locked: unlockResponse.metadata?.locked || false,
          signatureInfo: unlockResponse.metadata || null,
          loading: false
        }));

        // Remove read-only styling from cells
        applyCellStyling(false);

        // Reload the notebook to show the updated metadata
        await reloadNotebook();

        // CRITICAL: Notify NotebookLockManager about successful unlock
        if (lockManager) {
          await lockManager.handleUnlockSuccess();
        } else {
          console.warn('⚠️ No lockManager available - cells may not be properly unlocked');
        }

        // Show success popup similar to lock operation
        const metadata = unlockResponse.metadata;
        const unlockInfo = metadata.unlocked_by_user_name && metadata.unlock_timestamp
          ? `\nUnlocked by: ${metadata.unlocked_by_user_name} at ${new Date(metadata.unlock_timestamp).toLocaleString()}`
          : '';

        alert(`Notebook unlocked successfully!\nCommit: ${unlockResponse.commit_hash?.substring(0, 8)}\nSigned: ${unlockResponse.was_gpg_signed ? 'Yes' : 'No'}\nLocked: No${unlockInfo}`);

      } else {
        const errorMessage = unlockResponse.error || 'Failed to unlock notebook';
        setState(prev => ({
          ...prev,
          error: errorMessage,
          loading: false
        }));

        showErrorMessage('Unlock Error', errorMessage);
      }
    } catch (error: any) {
      const errorMessage = `Error unlocking notebook: ${error.message}`;
      setState(prev => ({
        ...prev,
        error: errorMessage,
        loading: false
      }));

      showErrorMessage('Lock/Unlock Error', errorMessage);
    }
  };

  /**
   * Handle commit message change.
   */
  const handleMessageChange = (event: React.ChangeEvent<HTMLTextAreaElement>): void => {
    setDialogState(prev => ({
      ...prev,
      commitMessage: event.target.value
    }));
  };

  /**
   * Handle lock confirmation.
   */
  const handleLockConfirm = async (): Promise<void> => {
    if (!dialogState.commitMessage.trim()) {
      alert('Please enter a commit message');
      return;
    }

    setDialogState(prev => ({ ...prev, isProcessing: true }));
    setState(prev => ({ ...prev, loading: true, error: null }));

    let originalNotebookContent: any = null;

    try {
      // Get notebook content and path
      const notebookPath = getAbsoluteNotebookPathSync(notebookPanel.context.path);
      originalNotebookContent = notebookPanel.content.model?.toJSON();

      if (!originalNotebookContent) {
        throw new Error('Could not get notebook content');
      }

      // Step 1: Add lock metadata to notebook content BEFORE committing
      const timestamp = new Date().toISOString();
      const lockMetadata = {
        locked: true,
        user_name: 'Unknown', // Will be updated by backend
        user_email: 'unknown@example.com', // Will be updated by backend
        timestamp: timestamp,
        commit_message: dialogState.commitMessage.trim(),
        content_hash: '', // Will be calculated by backend
        commit_hash: '', // Will be updated after commit
        commit_signed: false // Will be updated after commit
      };

      // Create updated notebook content with metadata
      const updatedNotebookContent = {
        ...originalNotebookContent,
        metadata: {
          ...originalNotebookContent.metadata,
          git_lock_sign: lockMetadata
        }
      };

      // Step 2: Save notebook with metadata
      try {
        // Update the notebook model with metadata
        notebookPanel.content.model?.fromJSON(updatedNotebookContent);

        // Save the notebook
        await notebookPanel.context.save();
      } catch (saveError) {
        throw new Error(`Failed to save notebook with metadata: ${saveError}`);
      }

      // Step 3: Call backend to lock notebook (backend will commit AND lock in one operation)
      const lockResponse = await gitLockSignAPI.lockNotebook(notebookPath, updatedNotebookContent, dialogState.commitMessage.trim());
      if (lockResponse.success) {
        setState(prev => ({
          ...prev,
          locked: true,
          signatureInfo: lockResponse.metadata || null,
          loading: false
        }));

        // Apply read-only styling to cells
        applyCellStyling(true);

        // Reload notebook to sync with updated metadata from backend
        await reloadNotebook();

        // CRITICAL: Notify NotebookLockManager about successful lock
        if (lockManager && lockResponse.metadata) {
          await lockManager.handleLockSuccess(lockResponse.metadata);
        } else {
          console.warn('⚠️ No lockManager available or no metadata - cells may not be properly locked');
        }

        // Show success message
        alert(`Notebook locked and committed successfully!\nCommit: ${lockResponse.commit_hash?.substring(0, 8)}\nSigned: ${lockResponse.signed ? 'Yes' : 'No'}\nLocked: Yes`);

        console.log('✅ Notebook locked and committed successfully');
      } else {
        // Rollback: restore original notebook content
        notebookPanel.content.model?.fromJSON(originalNotebookContent);
        await notebookPanel.context.save();
        throw new Error(lockResponse.error || 'Failed to lock notebook');
      }

    } catch (error) {
      console.error('❌ Lock operation error:', error);
      alert(`Error locking notebook: ${error}`);

      // Rollback: restore original notebook content if we have it
      if (originalNotebookContent && notebookPanel.content.model) {
        try {
          notebookPanel.content.model.fromJSON(originalNotebookContent);
          await notebookPanel.context.save();
        } catch (rollbackError) {
          console.error('❌ Failed to rollback notebook content:', rollbackError);
        }
      }

      setState(prev => ({ ...prev, loading: false }));
    } finally {
      setDialogState({
        showDialog: false,
        commitMessage: '',
        isProcessing: false
      });
    }
  };

  /**
   * Handle lock cancellation.
   */
  const handleLockCancel = (): void => {
    setDialogState({
      showDialog: false,
      commitMessage: '',
      isProcessing: false
    });
  };

  /**
   * Render the lock dialog.
   */
  const renderDialog = (): JSX.Element | null => {
    if (!dialogState.showDialog) {
      return null;
    }

    return (
      <div className="commit-dialog-overlay">
        <div className="commit-dialog">
          <div className="commit-dialog-header">
            <h3>Lock and Sign Notebook</h3>
          </div>
          <div className="commit-dialog-content">
            <label htmlFor="lock-commit-message">Commit Message:</label>
            <textarea
              id="lock-commit-message"
              value={dialogState.commitMessage}
              onChange={handleMessageChange}
              placeholder="Enter commit message..."
              rows={3}
              autoFocus
            />
          </div>
          <div className="commit-dialog-actions">
            <button
              className="commit-dialog-btn commit-dialog-btn-cancel"
              onClick={handleLockCancel}
              disabled={dialogState.isProcessing}
            >
              Cancel
            </button>
            <button
              className="commit-dialog-btn commit-dialog-btn-confirm"
              onClick={handleLockConfirm}
              disabled={dialogState.isProcessing || !dialogState.commitMessage.trim()}
            >
              {dialogState.isProcessing ? 'Locking...' : 'Lock'}
            </button>
          </div>
        </div>
      </div>
    );
  };

  /**
   * Reload the notebook from disk to sync with backend changes.
   */
  const reloadNotebook = async (): Promise<void> => {
    try {
      // Try multiple reload approaches
      try {
        // Method 1: Use context.revert() to reload from disk
        await notebookPanel.context.revert();
      } catch (revertError) {
        // Method 2: Try context.reload() if available
        if ('reload' in notebookPanel.context && typeof notebookPanel.context.reload === 'function') {
          await (notebookPanel.context as any).reload();
        } else {
          throw revertError;
        }
      }
    } catch (error) {
      console.warn('⚠️ Failed to reload notebook, but git operation was successful:', error);
      // Don't throw error - the operation was successful, reload is just for UX
    }
  };

  /**
   * Apply or remove read-only styling to notebook cells.
   */
  const applyCellStyling = (locked: boolean): void => {
    if (!notebookPanel?.content) {
      return;
    }

    const notebook = notebookPanel.content;
    const cells = notebook.widgets;

    cells.forEach(cell => {
      if (locked) {
        cell.node.classList.add('git-lock-sign-locked');
        cell.readOnly = true;
      } else {
        cell.node.classList.remove('git-lock-sign-locked');
        cell.readOnly = false;
      }
    });
  };

  /**
   * Get button text based on current state.
   */
  const getButtonText = (): string => {
    if (state.loading) {
      return state.locked ? 'Unlocking...' : 'Locking...';
    }
    return state.locked ? 'Unlock' : 'Lock';
  };

  /**
   * Get button icon based on current state.
   */
  const getButtonIcon = (): string => {
    if (state.loading) {
      return 'jp-CircularProgressIcon';
    }
    return state.locked ? 'jp-UnlockIcon' : 'jp-LockIcon';
  };

  /**
   * Get button title (tooltip) text.
   */
  const getButtonTitle = (): string => {
    if (state.signatureInfo) {
      const info = state.signatureInfo as any; // Cast to any to access new properties
      if (state.locked) {
        return `Locked by ${info.user_name} (${info.user_email}) at ${new Date(info.timestamp).toLocaleString()}`;
      } else if (info.unlocked_by_user_name) {
        return `Unlocked by ${info.unlocked_by_user_name} at ${new Date(info.unlock_timestamp).toLocaleString()}`;
      }
    }
    return state.locked ? 'Unlock notebook' : 'Lock and sign notebook';
  };

  // Don't render the button if disabled by configuration
  if (!state.shouldRender) {
    return null;
  }

  return (
    <>
      <button
        className={`git-lock-sign-button ${state.locked ? 'locked' : 'unlocked'} ${state.loading ? 'loading' : ''}`}
        onClick={handleLockClick}
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
      {renderDialog()}
    </>
  );
};

/**
 * Widget wrapper for the LockButton component.
 */
export class LockButtonWidget extends ReactWidget {
  private _notebookPanel: NotebookPanel;
  private _onStateChange?: (state: ILockButtonState) => void;
  private _lockManager?: NotebookLockManager;

  constructor(
    notebookPanel: NotebookPanel,
    onStateChange?: (state: ILockButtonState) => void,
    lockManager?: NotebookLockManager
  ) {
    super();
    this._notebookPanel = notebookPanel;
    this._onStateChange = onStateChange;
    this._lockManager = lockManager;
    this.addClass('git-lock-sign-lock-button-widget');
  }

  protected render(): JSX.Element {
    return (
      <LockButtonComponent
        notebookPanel={this._notebookPanel}
        onStateChange={this._onStateChange}
        lockManager={this._lockManager}
      />
    );
  }
}
