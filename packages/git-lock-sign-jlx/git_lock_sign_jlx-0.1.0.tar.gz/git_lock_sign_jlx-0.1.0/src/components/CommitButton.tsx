/**
 * Commit button component for staging and committing notebook changes.
 */

import React, { useState, useEffect } from 'react';

import { ReactWidget } from '@jupyterlab/apputils';
import { NotebookPanel } from '@jupyterlab/notebook';

import { gitLockSignAPI, getAbsoluteNotebookPathSync, stripRTCPrefix } from '../services/api';

/**
 * Props for the CommitButton component.
 */
interface ICommitButtonProps {
  notebookPanel: NotebookPanel;
}

/**
 * State for the commit button.
 */
interface ICommitButtonState {
  loading: boolean;
  lastCommitHash: string | null;
  error: string | null;
  shouldRender: boolean;
}

/**
 * State for the commit dialog.
 */
interface ICommitDialogState {
  showDialog: boolean;
  commitMessage: string;
  isProcessing: boolean;
}

/**
 * React component for committing notebook changes.
 */
const CommitButtonComponent: React.FC<ICommitButtonProps> = ({
  notebookPanel
}) => {
  const [state, setState] = useState<ICommitButtonState>({
    loading: false,
    lastCommitHash: null,
    error: null,
    shouldRender: true // Default to visible until config is loaded
  });

  const [dialogState, setDialogState] = useState<ICommitDialogState>({
    showDialog: false,
    commitMessage: '',
    isProcessing: false
  });

  // Load button configuration on component mount
  useEffect(() => {
    const loadButtonConfig = async () => {
      try {
        const config = await gitLockSignAPI.getConfig();
        setState(prev => ({
          ...prev,
          shouldRender: config.enable_commit_button ?? true
        }));
      } catch (error) {
        console.error('❌ Failed to load button configuration:', error);
        // Keep default visible state on error
      }
    };

    loadButtonConfig();
  }, []);

  /**
   * Handle commit button click.
   */
  const handleCommitClick = (): void => {
    // Don't proceed if loading
    if (state.loading) {
      return;
    }

    // Generate default commit message
    const notebookName = stripRTCPrefix(notebookPanel.context.path).split('/').pop() || 'notebook';
    const timestamp = new Date().toLocaleString();
    const defaultMessage = `Update ${notebookName} - ${timestamp}`;

    setDialogState({
      showDialog: true,
      commitMessage: defaultMessage,
      isProcessing: false
    });
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
   * Handle commit confirmation.
   */
  const handleCommitConfirm = async (): Promise<void> => {
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

      // Step 1: Add commit metadata to notebook content BEFORE committing
      const timestamp = new Date().toISOString();
      const commitMetadata = {
        locked: false, // This is just a commit, not a lock
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
          git_lock_sign: commitMetadata
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

      // Step 3: Commit the notebook (now includes metadata)
      const response = await gitLockSignAPI.commitNotebook({
        notebook_path: notebookPath,
        notebook_content: updatedNotebookContent,
        commit_message: dialogState.commitMessage.trim()
      });

      if (!response.success) {
        // Rollback: restore original notebook content
        notebookPanel.content.model?.fromJSON(originalNotebookContent);
        await notebookPanel.context.save();
        throw new Error(response.error || 'Failed to commit notebook');
      }

      setState(prev => ({
        ...prev,
        lastCommitHash: response.commit_hash || null,
        loading: false
      }));

      // Reload notebook to sync with updated metadata from backend
      await reloadNotebook();

      // Show success message
      alert(`Notebook committed successfully!\nCommit: ${response.commit_hash?.substring(0, 8)}\nSigned: ${response.signed ? 'Yes' : 'No'}`);

      console.log('✅ Notebook committed successfully');

    } catch (error) {
      console.error('❌ Commit operation error:', error);
      alert(`Error committing notebook: ${error}`);

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
   * Handle commit cancellation.
   */
  const handleCommitCancel = (): void => {
    setDialogState({
      showDialog: false,
      commitMessage: '',
      isProcessing: false
    });
  };

  /**
   * Render the commit dialog.
   */
  const renderDialog = (): JSX.Element | null => {
    if (!dialogState.showDialog) {
      return null;
    }

    return (
      <div className="commit-dialog-overlay">
        <div className="commit-dialog">
          <div className="commit-dialog-header">
            <h3>Commit Notebook</h3>
          </div>
          <div className="commit-dialog-content">
            <label htmlFor="commit-message">Commit Message:</label>
            <textarea
              id="commit-message"
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
              onClick={handleCommitCancel}
              disabled={dialogState.isProcessing}
            >
              Cancel
            </button>
            <button
              className="commit-dialog-btn commit-dialog-btn-confirm"
              onClick={handleCommitConfirm}
              disabled={dialogState.isProcessing || !dialogState.commitMessage.trim()}
            >
              {dialogState.isProcessing ? 'Committing...' : 'Commit'}
            </button>
          </div>
        </div>
      </div>
    );
  };

  // Don't render the button if disabled by configuration
  if (!state.shouldRender) {
    return null;
  }

  return (
    <>
      <button
        className={`git-lock-sign-button commit ${state.loading ? 'loading' : ''}`}
        onClick={handleCommitClick}
        disabled={state.loading}
        title="Commit notebook changes"
      >
        <span className={`jp-Icon ${state.loading ? 'jp-CircularProgressIcon' : 'jp-GitIcon'}`} />
        <span className="button-text">{state.loading ? 'Committing...' : 'Commit'}</span>
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
 * Widget wrapper for the CommitButton component.
 */
export class CommitButtonWidget extends ReactWidget {
  private _notebookPanel: NotebookPanel;

  constructor(notebookPanel: NotebookPanel) {
    super();
    this._notebookPanel = notebookPanel;
    this.addClass('git-lock-sign-commit-widget');
  }

  protected render(): JSX.Element {
    return (
      <CommitButtonComponent
        notebookPanel={this._notebookPanel}
      />
    );
  }
}
