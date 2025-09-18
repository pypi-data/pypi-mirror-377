/**
 * Notebook lock manager component for handling notebook-level locking state.
 */

import { IDisposable } from '@lumino/disposable';
import { Signal } from '@lumino/signaling';
import { showDialog, Dialog } from '@jupyterlab/apputils';

import { NotebookPanel } from '@jupyterlab/notebook';
import { Cell, CodeCell, ICodeCellModel } from '@jupyterlab/cells';

import { gitLockSignAPI, getAbsoluteNotebookPath, getAbsoluteNotebookPathSync, stripRTCPrefix } from '../services/api';
import { ServerConnection } from '@jupyterlab/services';
import {
  INotebookLockManager,
  ISignatureMetadata,
  INotebookStatus,
  IUserInfo
} from '../types';
import { JupyterFrontEnd } from '@jupyterlab/application';

/**
 * Notebook lock manager implementation for handling lock state and operations.
 */
export class NotebookLockManager implements INotebookLockManager, IDisposable {
  private _notebookPanel: NotebookPanel;
  private _app: JupyterFrontEnd;
  private _fileLifecycleTracker: any; // Using any to avoid import issues
  private _isLocked: boolean = false;
  private _signatureMetadata: ISignatureMetadata | null = null;
  private _isDisposed: boolean = false;
  private _stateChanged = new Signal<this, void>(this);
  public notificationSignal = new Signal<this, { msg: string; type: 'success' | 'error' }>(this);

  // Auto-operation tracking
  private _autoOperationsEnabled: boolean = true;
  private _executionCount: number = 0;

  // Track execution counts per cell to detect actual executions
  private _cellExecutionCounts = new Map<string, number>();

  // Disabled keyboard shortcuts when notebook is locked
  private _disabledShortcuts = [
    // Cell creation and structure
    { key: 'Enter', ctrlKey: false, shiftKey: false, altKey: false, description: 'Enter edit mode' },
    { key: 'a', ctrlKey: false, shiftKey: false, altKey: false, description: 'Insert cell above' },
    { key: 'b', ctrlKey: false, shiftKey: false, altKey: false, description: 'Insert cell below' },
    { key: 'm', ctrlKey: false, shiftKey: false, altKey: false, description: 'Change to Markdown' },
    { key: 'y', ctrlKey: false, shiftKey: false, altKey: false, description: 'Change to code' },

    // Cell selection and manipulation
    { key: 'ArrowUp', ctrlKey: false, shiftKey: true, altKey: false, description: 'Extend selection up' },
    { key: 'ArrowDown', ctrlKey: false, shiftKey: true, altKey: false, description: 'Extend selection down' },
    { key: 'a', ctrlKey: true, shiftKey: false, altKey: false, description: 'Select all cells' },
    { key: 'x', ctrlKey: false, shiftKey: false, altKey: false, description: 'Cut cell' },
    { key: 'c', ctrlKey: false, shiftKey: false, altKey: false, description: 'Copy cell' },
    { key: 'v', ctrlKey: false, shiftKey: false, altKey: false, description: 'Paste cell' },
    { key: 'm', ctrlKey: false, shiftKey: true, altKey: false, description: 'Merge cells' },
    { key: 'd', ctrlKey: false, shiftKey: false, altKey: false, description: 'Delete cell (first D)' },
    { key: 'z', ctrlKey: false, shiftKey: false, altKey: false, description: 'Undo cell action' },

    // Kernel operations
    { key: '0', ctrlKey: false, shiftKey: false, altKey: false, description: 'Restart kernel (first 0)' }
  ];

  // Auto-commit and auto-push timing configuration
  private _commitDebounceSeconds: number = 30; // Default value, will be updated from config
  private _pushDebounceSeconds: number = 120; // Default value, will be updated from config

  // Manual save detection and auto-push timing
  private _autoPushTimer: number | null = null;
  private _autoPushIntervalMinutes: number = 5; // Default, will be updated from config
  private _isManualSave: boolean = false;

  // Auto-push countdown for console logging
  private _autoPushCountdownInterval: number | null = null;
  private _autoPushTargetTime: number = 0;

  // Track activity to prevent unnecessary auto-pushes
  // Activity includes: cell execution, cell editing (NOT manual saves - they trigger immediate push)
  private _hasActivitySinceLastPush: boolean = false;

  constructor(notebookPanel: NotebookPanel, app: JupyterFrontEnd, fileLifecycleTracker?: any) {
    this._notebookPanel = notebookPanel;
    this._app = app;
    this._fileLifecycleTracker = fileLifecycleTracker;
    this._setupEventListeners();
    this._setupKeyboardOverrides();
    this._setupManualSaveDetection();
    this._checkInitialStatus();

    console.log('🚀 NotebookLockManager initialized');

    // Initialize the path cache and set up auto-operations
    this._initializeAsync();
  }

  private async _initializeAsync(): Promise<void> {
    try {
      // Initialize the server root cache by calling the async version once
      const relativePath = this._notebookPanel.context.path;
      await getAbsoluteNotebookPath(relativePath);
    } catch (error) {
      console.warn('⚠️ Failed to initialize server root cache:', error);
    }

    // Fetch configuration including debounce times
    await this._fetchConfiguration();

    // Set up auto-operations after cache is initialized
    this._setupAutoOperations();
  }

  /**
   * Fetch configuration from the sidecar service.
   */
  private async _fetchConfiguration(): Promise<void> {
    try {
      const config = await gitLockSignAPI.getConfig();

      if (config.success) {
        // Update configuration settings with values from sidecar
        this._commitDebounceSeconds = config.commit_debounce_seconds ?? 30;
        this._pushDebounceSeconds = config.push_debounce_seconds ?? 120;
        this._autoPushIntervalMinutes = config.auto_save_interval_minutes ?? 5;

        // Start the initial auto-push timer
        this._scheduleNextAutoPush();
      } else {
        console.warn('⚠️ Failed to fetch configuration, using defaults:', config.error);
      }
    } catch (error) {
      console.warn('⚠️ Failed to fetch configuration, using defaults:', error);
    }
  }

  /**
   * Signal emitted when the lock state changes.
   */
  get stateChanged(): Signal<this, void> {
    return this._stateChanged;
  }

  /**
   * Whether the notebook is currently locked.
   */
  get isLocked(): boolean {
    return this._isLocked;
  }

  /**
   * Current signature metadata, if any.
   */
  get signatureMetadata(): ISignatureMetadata | null {
    return this._signatureMetadata;
  }

  /**
   * Whether this manager has been disposed.
   */
  get isDisposed(): boolean {
    return this._isDisposed;
  }

  /**
   * Lock the notebook with GPG signature.
   */
  async lockNotebook(): Promise<boolean> {
    if (this._isDisposed || !this._notebookPanel.content?.model) {
      return false;
    }

    try {
      const notebookPath = getAbsoluteNotebookPathSync(this._notebookPanel.context.path);
      const notebookContent = this._notebookPanel.content.model.toJSON();

      console.log('🚀 Starting lock operation');
      const response = await gitLockSignAPI.lockNotebook(notebookPath, notebookContent);

      if (response.success && response.metadata) {
        this._isLocked = true;
        this._signatureMetadata = response.metadata;

        // Apply cell locking based on updated state (no revert needed!)
        this._applyCellLocking(true);
        await this.checkStatus();

        this._stateChanged.emit();
        return true;
      }

      return false;
    } catch (error) {
      console.error('❌ Lock operation error:', error);
      return false;
    }
  }

  /**
   * Unlock the notebook after signature verification.
   */
  async unlockNotebook(): Promise<boolean> {
    if (this._isDisposed || !this._notebookPanel.content?.model) {
      return false;
    }

    try {
      const notebookPath = getAbsoluteNotebookPathSync(this._notebookPanel.context.path);
      const notebookContent = this._notebookPanel.content.model.toJSON();

      const response = await gitLockSignAPI.unlockNotebook(notebookPath, notebookContent);

      if (response.success && response.metadata) {
        this._isLocked = response.metadata.locked;
        this._signatureMetadata = response.metadata;
        this._applyCellLocking(false);
        this.notificationSignal.emit({ msg: response.message || 'Notebook unlocked successfully!', type: 'success' });

        // State updated from API response - no revert needed!
        this._stateChanged.emit();
        return true;
      } else {
        const errorMessage = response.error || 'An unknown error occurred during unlock.';
        this.notificationSignal.emit({ msg: errorMessage, type: 'error' });
        showDialog({
          title: 'Unlock Failed',
          body: errorMessage,
          buttons: [Dialog.okButton({ label: 'OK' })]
        });
        return false;
      }
    } catch (error: any) {
      const errorMessage = error.message || 'An unexpected error occurred.';
      console.error('❌ Unlock operation error:', error);
      this.notificationSignal.emit({ msg: errorMessage, type: 'error' });
      showDialog({
        title: 'Unlock Error',
        body: `An unexpected error occurred: ${errorMessage}`,
        buttons: [Dialog.okButton({ label: 'OK' })]
      });
      return false;
    }
  }

  /**
   * Handle successful lock operation from LockButton.
   * This ensures immediate state synchronization after lock.
   */
  async handleLockSuccess(metadata: ISignatureMetadata): Promise<void> {
    console.log('✅ Lock success notification received');

    this._isLocked = true;
    this._signatureMetadata = metadata;

    this._applyCellLocking(true);
    this._stateChanged.emit();
  }

  /**
   * Handle successful unlock operation from LockButton.
   * This ensures immediate state synchronization after unlock.
   */
  async handleUnlockSuccess(): Promise<void> {
    console.log('🎯 NotebookLockManager: Handling unlock success notification from LockButton...');

    this._isLocked = false;
    this._signatureMetadata = null;

    console.log('🔓 NotebookLockManager: Removing read-only enforcement after unlock success...');
    this._applyCellLocking(false);

    this._stateChanged.emit();
    console.log('✅ NotebookLockManager: Unlock success handled - cells should now be editable');
  }

  /**
   * Check the current lock status of the notebook.
   */
  async checkStatus(): Promise<INotebookStatus> {
    if (this._isDisposed || !this._notebookPanel.content?.model) {
      return {
        locked: false,
        signature_valid: false,
        message: 'Notebook not available'
      };
    }

    try {
      const notebookContent = this._notebookPanel.content.model.toJSON();
      const notebookPath = getAbsoluteNotebookPathSync(this._notebookPanel.context.path);
      const response = await gitLockSignAPI.checkNotebookStatus(notebookContent, notebookPath);

      if (response.success) {
        // Update internal state
        this._isLocked = response.locked || false;
        this._signatureMetadata = response.metadata || null;

        // Apply cell locking based on status
        this._applyCellLocking(this._isLocked);

        this._stateChanged.emit();

        return {
          locked: response.locked || false,
          signature_valid: response.signature_valid || false,
          message: response.message || 'Status checked',
          metadata: response.metadata
        };
      }

      return {
        locked: false,
        signature_valid: false,
        message: response.error || 'Failed to check status'
      };
    } catch (error) {
      console.error('Error checking notebook status:', error);
      return {
        locked: false,
        signature_valid: false,
        message: `Error: ${error}`
      };
    }
  }

  /**
   * Get git user information.
   */
  async getUserInfo(): Promise<IUserInfo | null> {
    try {
      const notebookPath = getAbsoluteNotebookPathSync(this._notebookPanel.context.path);
      const userInfo = await gitLockSignAPI.getUserInfo(notebookPath);
      return userInfo.success
        ? {
            name: userInfo.user_name || '',
            email: userInfo.user_email || '',
            gpgKeyId: userInfo.gpg_key_id || ''
          }
        : null;
    } catch (error) {
      console.error('Error getting user info:', error);
      return null;
    }
  }

  /**
   * Commit the notebook to git.
   */
  async commitNotebook(): Promise<boolean> {
    if (this._isDisposed || !this._notebookPanel.content?.model) {
      return false;
    }

    try {
      const notebookPath = getAbsoluteNotebookPathSync(this._notebookPanel.context.path);
      const notebookContent = this._notebookPanel.content.model.toJSON();

      const request = {
        notebook_path: notebookPath,
        notebook_content: notebookContent,
        commit_message: '' // This should be set by the calling component
      };

      const response = await gitLockSignAPI.commitNotebook(request);

      if (response.success) {
        // Emit success notification
        this.notificationSignal.emit({
          msg: 'Notebook committed successfully',
          type: 'success'
        });
        return true;
      } else {
        // Emit error notification
        this.notificationSignal.emit({
          msg: response.error || 'Failed to commit notebook',
          type: 'error'
        });
        return false;
      }
    } catch (error) {
      // Emit error notification
      this.notificationSignal.emit({
        msg: `Error committing notebook: ${error}`,
        type: 'error'
      });
      return false;
    }
  }

  /**
   * Push notebook changes to remote repository.
   */
  async pushNotebook(): Promise<boolean> {
    if (this._isDisposed || !this._notebookPanel.content?.model) {
      return false;
    }

    try {
      const notebookPath = getAbsoluteNotebookPathSync(this._notebookPanel.context.path);

      // First provision the repository
      const provisionResponse = await gitLockSignAPI.provisionRepository(notebookPath);

      if (!provisionResponse.success) {
        this.notificationSignal.emit({
          msg: provisionResponse.error || 'Failed to provision repository',
          type: 'error'
        });
        return false;
      }

      const pushUrl = provisionResponse.push_url;
      if (!pushUrl) {
        this.notificationSignal.emit({
          msg: 'No push URL received from provision API',
          type: 'error'
        });
        return false;
      }

      // Then push to repository
      const pushResponse = await gitLockSignAPI.pushToRepository(notebookPath, pushUrl);

      if (pushResponse.success) {
        this.notificationSignal.emit({
          msg: `Successfully pushed to remote repository: ${provisionResponse.repo_url || 'GitLab server'}`,
          type: 'success'
        });
        return true;
      } else {
        this.notificationSignal.emit({
          msg: pushResponse.error || 'Failed to push to repository',
          type: 'error'
        });
        return false;
      }
    } catch (error) {
      this.notificationSignal.emit({
        msg: `Error pushing notebook: ${error}`,
        type: 'error'
      });
      return false;
    }
  }

  /**
   * Dispose of the notebook lock manager and clean up resources.
   */
  dispose(): void {
    if (this._isDisposed) {
      return;
    }

    console.log('🧹 Disposing notebook lock manager');

    this._isDisposed = true;

    // Trigger auto-push on file close if auto-operations are enabled
    this._triggerAutoPushOnClose();

    // Remove cell locking if currently locked
    if (this._isLocked) {
      this._applyCellLocking(false);
    }

    // Remove keyboard event listener
    document.removeEventListener('keydown', this._handleKeyDown, true);
    console.log('🎹 Keyboard override system disposed');

    // Clear auto-commit timeout
    if (this._autoCommitTimeout) {
      clearTimeout(this._autoCommitTimeout);
      this._autoCommitTimeout = null;
    }

    // Clear auto-push timer and countdown
    if (this._autoPushTimer) {
      clearTimeout(this._autoPushTimer);
      this._autoPushTimer = null;
    }
    if (this._autoPushCountdownInterval) {
      clearInterval(this._autoPushCountdownInterval);
      this._autoPushCountdownInterval = null;
    }

    // Clean up hash mismatch workaround
    if (this._hashMismatchObserver) {
      this._hashMismatchObserver.disconnect();
      this._hashMismatchObserver = null;
      // console.log('🛡️ [HASH-WORKAROUND] Hash mismatch observer disposed');
    }

    // Clean up periodic dialog check interval
    if (this._hashMismatchInterval) {
      clearInterval(this._hashMismatchInterval);
      this._hashMismatchInterval = null;
      // console.log('🛡️ [HASH-WORKAROUND] Hash mismatch interval disposed');
    }

    // Clear references
    this._cellExecutionCounts.clear();
    this._pendingAutoCommit = null;
    this._currentAutoOperation = null;
    this._signatureMetadata = null;
    Signal.clearData(this);

    console.log('✅ Notebook lock manager disposed successfully');
  }

  /**
   * Set up event listeners for notebook changes.
   */
  private _setupEventListeners(): void {
    // Listen for notebook content changes
    if (this._notebookPanel.content?.model) {
      this._notebookPanel.content.model.contentChanged.connect(
        this._onContentChanged,
        this
      );
    }

    // Listen for new cells being added
    if (this._notebookPanel.content) {
      this._notebookPanel.content.modelChanged.connect(
        this._onModelChanged,
        this
      );
    }
  }

  /**
   * Set up automatic operations for cell execution and notebook saving.
   */
  private _setupAutoOperations(): void {

    // Initialize git repository if needed
    this._initializeGitRepository();

    // Set up cell execution detection
    this._setupCellExecutionDetection();

    // Set up notebook save detection
    this._setupNotebookSaveDetection();

    console.log('✅ CELN auto-operations configured');
  }

  /**
   * Initialize git repository if the notebook is not in one.
   */
  private async _initializeGitRepository(): Promise<void> {
    try {
      const notebookPath = getAbsoluteNotebookPathSync(this._notebookPanel.context.path);

      // Check if already in a git repository
      const status = await gitLockSignAPI.getRepositoryStatus(notebookPath);

      if (!status.success || !status.is_git_repository) {
        console.warn('⚠️ Notebook is not in a git repository - this should have been set up during session initialization');
        // For backward compatibility, still try to initialize git repository
        
        const initResult = await gitLockSignAPI.initGitRepository(notebookPath);

        if (initResult.success) {
          console.log('✅ Git repository initialized successfully');
          this._showNotification('Git repository initialized for automatic tracking', 'success');
          
          // Since this is a fallback, also try to provision
          await this._fallbackProvision(notebookPath);
        } else {
          console.error('❌ [NOTEBOOK] Failed to initialize git repository:', initResult.error);
          this._showNotification('Failed to initialize git repository', 'error');
          return;
        }
      } else {
      }

    } catch (error) {
      console.error('[NOTEBOOK] Error checking git repository:', error);
      this._showNotification('Git repository check failed', 'error');
    }
  }

  /**
   * Fallback provision when notebook is not in a session-initialized repository.
   */
  private async _fallbackProvision(notebookPath: string): Promise<void> {
    try {

      const provisionResult = await gitLockSignAPI.provisionRepository(notebookPath);

      if (provisionResult.success) {
        console.log('✅ Fallback GitLab integration provisioned successfully');

        // Print the repository URL to terminal for user reference
        if (provisionResult.repo_url) {
        }

        this._showNotification('GitLab integration configured', 'success');
      } else {
        console.warn('⚠️ [NOTEBOOK] Fallback GitLab provisioning failed (will retry on push):', provisionResult.error);
        this._showNotification('GitLab integration will be configured on first push', 'success');
      }
    } catch (error) {
      console.warn('⚠️ [NOTEBOOK] Fallback GitLab provisioning failed (will retry on push):', error);
      // Don't show error notification as this is not critical - it will retry on push
    }
  }

  /**
   * Set up detection of cell execution events.
   */
  private _setupCellExecutionDetection(): void {

    // Set up initial execution count monitoring
    this._setupExecutionCountMonitoring();

    // Monitor for new cells being added to the notebook
    const notebookContent = this._notebookPanel.content;
    if (notebookContent && notebookContent.model) {
      notebookContent.model.cells.changed.connect(() => {
        console.log('📱 Notebook cells changed, re-setting up execution monitoring');
        // Re-setup monitoring for new cells
        this._setupExecutionCountMonitoring();
      });
    }
  }

  /**
   * Set up execution count monitoring for all code cells.
   */
  private _setupExecutionCountMonitoring(): void {
    const notebook = this._notebookPanel.content;
    if (!notebook) {
      console.log('⚠️ No notebook content available');
      return;
    }

    const cells = notebook.widgets;

    cells.forEach((cell, index) => {
      if (cell.model.type === 'code') {
        this._setupCellExecutionMonitoring(cell as CodeCell, index);
      }
    });
  }

  /**
   * Set up execution count monitoring for a specific cell.
   */
  private _setupCellExecutionMonitoring(codeCell: CodeCell, cellIndex: number): void {
    const cellId = codeCell.model.id;
    const codeModel = codeCell.model as ICodeCellModel;
    const currentExecutionCount = codeModel.executionCount || 0;

    // Initialize or update the execution count for this cell
    this._cellExecutionCounts.set(cellId, currentExecutionCount);


    // Listen for execution count changes on this specific cell using the correct signal signature
    codeModel.stateChanged.connect((sender, args) => {
      if (args.name === 'executionCount') {
        const newExecutionCount = codeModel.executionCount;
        const oldExecutionCount = this._cellExecutionCounts.get(cellId) || 0;

        console.log(`🎯 Cell ${cellIndex} execution count changed: ${oldExecutionCount} -> ${newExecutionCount}`);

        // Only trigger if execution count actually increased (real execution)
        if (newExecutionCount && newExecutionCount > oldExecutionCount) {
          console.log(`✅ Detected actual cell execution for cell ${cellIndex}`);

          // Update our tracking
          this._cellExecutionCounts.set(cellId, newExecutionCount);
          this._executionCount++;

          console.log(`📊 Total execution count: ${this._executionCount}`);

          // Trigger auto-commit for this real execution
          this._handleCellExecutionCompleted(cellIndex, cellId);
        } else if (newExecutionCount && newExecutionCount <= oldExecutionCount) {
          console.log(`⏸️ Execution count didn't increase, likely not a new execution`);
        }
      }
    });
  }


  /**
   * Set up manual save detection by hooking into JupyterLab commands.
   */
  private _setupManualSaveDetection(): void {

    // Hook into the 'docmanager:save' command to detect manual saves
    this._app.commands.commandExecuted.connect((sender, args) => {
      if (args.id === 'docmanager:save' || args.id === 'notebook:save-notebook') {
        const current = this._app.shell.currentWidget;
        if (current === this._notebookPanel) {
           this._isManualSave = true;
           this._resetAutoPushTimer();
        }
      }
    });

    // Also listen for Ctrl+S key combination
    document.addEventListener('keydown', (event) => {
      if (event.ctrlKey && event.key === 's') {
        const current = this._app.shell.currentWidget;
        if (current === this._notebookPanel) {
           this._isManualSave = true;
           this._resetAutoPushTimer();
        }
      }
    });

  }

  /**
   * Reset the auto-push timer (called when manual save is detected).
   */
  private _resetAutoPushTimer(): void {

    // Clear existing timer and countdown
    if (this._autoPushTimer) {
      clearTimeout(this._autoPushTimer);
    }
    if (this._autoPushCountdownInterval) {
      clearInterval(this._autoPushCountdownInterval);
    }

    // Set new timer for the configured interval
    const intervalMs = this._autoPushIntervalMinutes * 60 * 1000;
    this._autoPushTargetTime = Date.now() + intervalMs;

    this._autoPushTimer = setTimeout(() => {
      this._handleScheduledAutoPush();
    }, intervalMs);

    // Start countdown logging (every 30 seconds = 0.5 minutes)
    this._startAutoPushCountdown();

  }

  /**
   * Schedule the next auto-push (called after a scheduled auto-push completes).
   */
  private _scheduleNextAutoPush(): void {

    // Clear existing timer and countdown
    if (this._autoPushTimer) {
      clearTimeout(this._autoPushTimer);
    }
    if (this._autoPushCountdownInterval) {
      clearInterval(this._autoPushCountdownInterval);
    }

    // Set new timer for the configured interval
    const intervalMs = this._autoPushIntervalMinutes * 60 * 1000;
    this._autoPushTargetTime = Date.now() + intervalMs;

    this._autoPushTimer = setTimeout(() => {
      this._handleScheduledAutoPush();
    }, intervalMs);

    // Start countdown logging
    this._startAutoPushCountdown();

  }

  /**
   * Start the auto-push countdown logging.
   */
  private _startAutoPushCountdown(): void {
    // Clear any existing countdown
    if (this._autoPushCountdownInterval) {
      clearInterval(this._autoPushCountdownInterval);
    }

    // Log initial countdown
    this._logAutoPushCountdown();

    // Set up interval to log countdown every 30 seconds (0.5 minutes)
    this._autoPushCountdownInterval = setInterval(() => {
      this._logAutoPushCountdown();
    }, 30000); // 30 seconds
  }

  /**
   * Log the current auto-push countdown.
   */
  private _logAutoPushCountdown(): void {
    if (this._autoPushTargetTime <= 0) {
      return;
    }

    const now = Date.now();
    const remainingMs = this._autoPushTargetTime - now;

    if (remainingMs <= 0) {
      // Clear the countdown since timer has expired
      if (this._autoPushCountdownInterval) {
        clearInterval(this._autoPushCountdownInterval);
        this._autoPushCountdownInterval = null;
      }
      return;
    }

    const remainingMinutes = remainingMs / (60 * 1000);

    if (remainingMinutes >= 1) {
    } else {
    }
  }

  /**
   * Handle scheduled auto-push (triggered by timer).
   */
  private async _handleScheduledAutoPush(): Promise<void> {
    console.log('🚀 Starting scheduled auto-push');

    // Clear the countdown since we're executing now
    if (this._autoPushCountdownInterval) {
      clearInterval(this._autoPushCountdownInterval);
      this._autoPushCountdownInterval = null;
    }

    if (!this._autoOperationsEnabled) {
      return;
    }

    let pushSuccessful = false;

    try {
      const notebookPath = getAbsoluteNotebookPathSync(this._notebookPanel.context.path);
      const result = await gitLockSignAPI.autoPush(notebookPath);

      if (result.success) {
        pushSuccessful = true;
        if (result.debounced) {
          console.log('⏱️ Push debounced - no changes to push');
          // Don't schedule next auto-push if nothing was pushed due to debouncing
          return;
        } else {
          console.log('✅ Scheduled auto-push completed successfully');
          this._showNotification('Scheduled auto-push: Changes synchronized', 'success');
          // Reset activity flag since we just pushed all changes
          this._hasActivitySinceLastPush = false;
        }
      } else {
        console.error('❌ [SCHEDULED-AUTO-PUSH] Scheduled auto-push failed:', result.error);
      }
    } catch (error) {
      console.error('❌ [SCHEDULED-AUTO-PUSH] Error during scheduled auto-push:', error);
    }

    // Only schedule the next auto-push if there's been activity since last push or if we need to retry on failure
    if (this._hasActivitySinceLastPush || !pushSuccessful) {
      this._scheduleNextAutoPush();
    } else {
    }
  }

  /**
   * Trigger auto-push when the notebook is being closed.
   * This runs completely asynchronously and doesn't block the disposal process.
   */
  private _triggerAutoPushOnClose(): void {
    if (!this._autoOperationsEnabled) {
      console.log('⏸️ [AUTO-PUSH-ON-CLOSE] Auto-operations disabled, skipping auto-push on close');
      return;
    }

    // Check if file deletion auto-push is already in progress to avoid duplicates
    if (this._fileLifecycleTracker?.isDeletionPushInProgress?.(this._notebookPanel.context.path)) {
      console.log('🚫 [AUTO-PUSH-ON-CLOSE] File deletion auto-push already in progress, skipping duplicate push');
      return;
    }

    console.log('🚪 [AUTO-PUSH-ON-CLOSE] Triggering auto-push before closing notebook...');

    // Execute auto-push completely asynchronously without any timeout
    // This allows the push to complete naturally even if it takes time
    const executePushOnClose = async () => {
      try {
        const notebookPath = getAbsoluteNotebookPathSync(this._notebookPanel.context.path);
        
        
        const result = await gitLockSignAPI.autoPush(notebookPath);

        
        if (result.success) {
          if (result.debounced) {
            console.log('⏱️ [AUTO-PUSH-ON-CLOSE] Push debounced - no changes to push on close');
          } else {
            console.log('✅ [AUTO-PUSH-ON-CLOSE] Auto-push on close completed successfully');
            if (result.repository_url) {
              console.log('🔗 [AUTO-PUSH-ON-CLOSE] Repository URL:', result.repository_url);
            }
          }
        } else {
          console.warn('⚠️ [AUTO-PUSH-ON-CLOSE] Auto-push on close failed:', result.error);
        }
      } catch (error) {
        console.warn('⚠️ [AUTO-PUSH-ON-CLOSE] Error during auto-push on close:', error);
      }
    };

    // Execute without awaiting to avoid blocking disposal
    executePushOnClose();
  }

  /**
   * Set up detection of notebook save events.
   */
  private _setupNotebookSaveDetection(): void {

    // Set up hash mismatch dialog auto-dismissal as a workaround
    this._setupHashMismatchWorkaround();

    // Listen for save state changes
    this._notebookPanel.context.saveState.connect(async (context, saveState) => {

      if (saveState === 'started') {
        // Wait for any ongoing auto-operations to complete before starting save
        if (this._currentAutoOperation) {
          console.log('⏳ [SAVE-DEBUG] Waiting for ongoing auto-operation to complete before save...');
          try {
            await this._currentAutoOperation;
            console.log('✅ [SAVE-DEBUG] Auto-operation completed, proceeding with save');
          } catch (error) {
            console.log('⚠️ [SAVE-DEBUG] Auto-operation failed, proceeding with save anyway:', error);
          }
        }

        this._saveInProgress = true;
        console.log('🚀 [SAVE-DEBUG] Save STARTED - blocking new auto-operations to prevent interference');
        this._debugNotebookContent('SAVE-STARTED');
      } else if (saveState === 'completed') {

        // Debug content immediately after save completion
        this._debugNotebookContent('SAVE-COMPLETED');

        // Add a longer delay to ensure JupyterLab has completely finished all save operations
        setTimeout(() => {
          this._debugNotebookContent('PRE-AUTO-PUSH');
          this._saveInProgress = false; // Clear the flag before auto-operations
          this._handleNotebookSaveCompleted();
        }, 1000); // Increased to 1000ms delay

        return; // Don't call immediately
      } else if (saveState === 'failed') {
        this._saveInProgress = false; // Clear flag on save failure
        console.log('❌ [SAVE-DEBUG] Save FAILED - clearing save-in-progress flag');
      }
    });

    console.log('✅ [NotebookLockManager] Save detection setup complete');
  }

  /**
   * Set up automatic dismissal of hash mismatch dialogs as a temporary workaround.
   */
  private _setupHashMismatchWorkaround(): void {
    console.log('🛡️ [HASH-WORKAROUND] Setting up automatic hash mismatch dialog dismissal...');

    // Monitor for hash mismatch dialogs and auto-dismiss them
    this._hashMismatchObserver = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            const element = node as Element;

            // Debug: Log all dialogs that appear
            // const allDialogs = element.querySelectorAll('.jp-Dialog, .lm-Widget.jp-Dialog, [role="dialog"]');
            // if (allDialogs.length > 0) {
            //   console.log('🔍 [HASH-WORKAROUND] Found dialog elements:', allDialogs.length);
            //   allDialogs.forEach((dialog, index) => {
            //     const dialogText = dialog.textContent || '';
            //     console.log(`🔍 [HASH-WORKAROUND] Dialog ${index} text:`, dialogText.substring(0, 200));
            //     console.log(`🔍 [HASH-WORKAROUND] Dialog ${index} classes:`, dialog.className);
            //   });
            // }

            // Also check if the element itself is a dialog
            if (element.matches && (element.matches('.jp-Dialog') || element.matches('[role="dialog"]'))) {
              // console.log('🔍 [HASH-WORKAROUND] Root element is a dialog');
              const dialogText = element.textContent || '';
              console.log('🔍 [HASH-WORKAROUND] Root dialog text:', dialogText.substring(0, 200));
            }

            // Look for JupyterLab dialog elements that contain hash mismatch warnings
            const dialogs = element.querySelectorAll('.jp-Dialog, .lm-Widget.jp-Dialog, [role="dialog"]');
            dialogs.forEach((dialog) => {
              const dialogText = dialog.textContent || '';

                             // Check if this is a hash mismatch dialog with more comprehensive text matching
               if (dialogText.includes('Different hash found') ||
                   dialogText.includes('file seems to have been saved') ||
                   dialogText.includes('while the current file seems to have been saved') ||
                   dialogText.includes('Last saving performed') ||
                   dialogText.includes('File Changed') ||
                   dialogText.includes('has changed on disk') ||
                   dialogText.includes('Do you want to overwrite') ||
                   dialogText.includes('hash') ||
                   dialogText.includes('conflict') ||
                   dialogText.includes('overwrite')) {

                console.log('🚨 [HASH-WORKAROUND] Hash mismatch dialog detected!');
                console.log('🚨 [HASH-WORKAROUND] Full dialog text:', dialogText);

                // Look for "Overwrite" or "OK" button and click it
                const buttons = dialog.querySelectorAll('button');
                console.log('🔍 [HASH-WORKAROUND] Found buttons:', buttons.length);

                buttons.forEach((btn, index) => {
                  console.log(`🔍 [HASH-WORKAROUND] Button ${index}:`, btn.textContent, btn.className);
                });

                // Try to find the right button to click
                const overwriteBtn = dialog.querySelector('button[data-value="overwrite"], button[data-value="1"], .jp-mod-accept, button:contains("Overwrite"), button:contains("OK")') as HTMLButtonElement;
                if (overwriteBtn) {
                  console.log('✅ [HASH-WORKAROUND] Clicking Overwrite button automatically');
                  setTimeout(() => overwriteBtn.click(), 100);
                  return;
                }

                // Fallback: Click the last button (usually the primary action)
                const allButtons = dialog.querySelectorAll('button');
                if (allButtons.length > 0) {
                  const lastBtn = allButtons[allButtons.length - 1] as HTMLButtonElement;
                  console.log('✅ [HASH-WORKAROUND] Clicking last button automatically:', lastBtn.textContent);
                  setTimeout(() => lastBtn.click(), 100);
                  return;
                }

                console.log('⚠️ [HASH-WORKAROUND] Could not find button to auto-dismiss dialog');
              }
            });
          }
        });
      });
    });

    // Start observing
    this._hashMismatchObserver.observe(document.body, {
      childList: true,
      subtree: true
    });

    // Also add a periodic check for existing dialogs (backup method)
    const periodicCheck = () => {
      const existingDialogs = document.querySelectorAll('.jp-Dialog, .lm-Widget.jp-Dialog, [role="dialog"]');
      if (existingDialogs.length > 0) {
        // console.log('🔍 [HASH-WORKAROUND] Periodic check found existing dialogs:', existingDialogs.length);
        existingDialogs.forEach((dialog, index) => {
          const dialogText = dialog.textContent || '';
          // console.log(`🔍 [HASH-WORKAROUND] Existing dialog ${index}:`, dialogText.substring(0, 200));

                     // Check for hash mismatch dialogs
           if (dialogText.includes('Different hash found') ||
               dialogText.includes('file seems to have been saved') ||
               dialogText.includes('Last saving performed') ||
               dialogText.includes('File Changed') ||
               dialogText.includes('has changed on disk') ||
               dialogText.includes('Do you want to overwrite') ||
               dialogText.includes('hash') ||
               dialogText.includes('conflict')) {

                         console.log('🚨 [HASH-WORKAROUND] Found existing hash mismatch dialog!');
             const buttons = dialog.querySelectorAll('button');
             console.log('🔍 [HASH-WORKAROUND] Found buttons in existing dialog:', buttons.length);

             // Debug all buttons found
             buttons.forEach((btn, index) => {
               console.log(`🔍 [HASH-WORKAROUND] Existing Button ${index}:`, btn.textContent, btn.className);
             });

             if (buttons.length > 0) {
               const lastBtn = buttons[buttons.length - 1] as HTMLButtonElement;
               console.log('✅ [HASH-WORKAROUND] Auto-clicking last button:', lastBtn.textContent);
               lastBtn.click();
             } else {
               console.log('⚠️ [HASH-WORKAROUND] No buttons found in existing dialog');

               // Try alternative button selectors
               const altButtons = dialog.querySelectorAll('input[type="button"], .jp-Dialog-button, [role="button"]');
               console.log('🔍 [HASH-WORKAROUND] Alternative button search found:', altButtons.length);
               if (altButtons.length > 0) {
                 const altBtn = altButtons[altButtons.length - 1] as HTMLElement;
                 console.log('✅ [HASH-WORKAROUND] Clicking alternative button:', altBtn.textContent);
                 altBtn.click();
               }
             }
          }
        });
      }
    };

    // Run periodic check every 2 seconds
    this._hashMismatchInterval = setInterval(periodicCheck, 2000);

    console.log('✅ [HASH-WORKAROUND] Hash mismatch auto-dismissal is now active (with periodic backup)');
  }

  /**
   * Debug notebook content at different stages
   */
  private _debugNotebookContent(stage: string): void {
    try {
      console.log(`📋 [${stage}] === Content Debug ===`);

      // Get content from model
      const modelContent = this._notebookPanel.content.model?.toJSON();
      if (modelContent) {
        const cells = (modelContent as any).cells;
        console.log(`📋 [${stage}] Model has ${cells?.length || 0} cells`);

        if (Array.isArray(cells)) {
          cells.forEach((cell: any, index: number) => {
            const source = Array.isArray(cell.source) ? cell.source.join('') : cell.source;
            console.log(`📋 [${stage}] Cell ${index}: "${source}" (type: ${cell.cell_type})`);
          });
        }
      } else {
        console.log(`📋 [${stage}] ❌ No model content available`);
      }

      // Check file on disk (if accessible)
      this._checkDiskContent(stage);

    } catch (error) {
      console.error(`📋 [${stage}] Error debugging content:`, error);
    }
  }

  /**
   * Check content on disk
   */
  private async _checkDiskContent(stage: string): Promise<void> {
    try {
      // Use a small delay to let file system operations complete
      setTimeout(async () => {
        try {
          // Strip RTC prefix from the path before making API call
          const cleanPath = stripRTCPrefix(this._notebookPanel.context.path);
          
          // Use proper JupyterLab contents manager instead of manual fetch
          const serverSettings = ServerConnection.makeSettings();
          const contentsManager = new (await import('@jupyterlab/services')).ContentsManager({
            serverSettings
          });
          
          const content = await contentsManager.get(cleanPath);
          
          if (content && content.content?.cells) {
            console.log(`💾 [${stage}] Disk has ${content.content.cells.length || 0} cells`);
            
            content.content.cells.forEach((cell: any, index: number) => {
              const source = Array.isArray(cell.source) ? cell.source.join('') : cell.source;
              console.log(`💾 [${stage}] Disk Cell ${index}: "${source}" (type: ${cell.cell_type})`);
            });
          } else {
            console.log(`💾 [${stage}] Could not read disk content or no cells found`);
          }
        } catch (error) {
          console.log(`💾 [${stage}] Error reading disk content:`, error);
        }
      }, 100);

    } catch (error) {
      console.log(`💾 [${stage}] Error checking disk content:`, error);
    }
  }

  // Flag to track pending auto-commit after cell execution
  private _pendingAutoCommit: {
    cellPreview: string;
    executionCount: number;
    cellIndex?: number;
    cellId?: string;
  } | null = null;

  // Timeout for fallback auto-commit if natural save doesn't occur
  private _autoCommitTimeout: number | null = null;

  // Flag to track if save is in progress to prevent interference
  private _saveInProgress = false;

  // Flag to track ongoing auto-operations
  private _autoOperationInProgress = false;

  // Promise to track ongoing auto-operations
  private _currentAutoOperation: Promise<void> | null = null;

  // Observer for hash mismatch dialog auto-dismissal
  private _hashMismatchObserver: MutationObserver | null = null;

  // Interval for periodic dialog checking
  private _hashMismatchInterval: number | null = null;

  /**
   * Handle cell execution completion - schedule auto-commit for next save.
   */
  private async _handleCellExecutionCompleted(cellIndex?: number, cellId?: string): Promise<void> {
    console.log('🚀 _handleCellExecutionCompleted called');
    console.log(`🔧 Auto-operations enabled: ${this._autoOperationsEnabled}`);

    if (!this._autoOperationsEnabled) {
      console.log('⏸️ Auto-operations disabled, skipping auto-commit');
      return;
    }

    if (this._saveInProgress) {
      console.log('⏸️ [AUTO-COMMIT] Save in progress, deferring auto-commit to prevent interference');
      // Note: The pending auto-commit will be handled when save completes
      return;
    }

    try {
      const notebookPath = getAbsoluteNotebookPathSync(this._notebookPanel.context.path);
      console.log(`📁 Notebook path: ${notebookPath}`);

      // Get preview of the last executed cell content
      const cellPreview = this._getLastExecutedCellPreview(cellIndex, cellId);
      console.log(`📝 Cell preview: "${cellPreview}"`);

      // Clear any existing timeout
      if (this._autoCommitTimeout) {
        clearTimeout(this._autoCommitTimeout);
        this._autoCommitTimeout = null;
      }

      // Instead of manually saving (which causes hash mismatch popup),
      // store the execution info and let JupyterLab handle the save naturally
      this._pendingAutoCommit = {
        cellPreview,
        executionCount: this._executionCount,
        cellIndex,
        cellId
      };

      // Mark activity since cell execution creates changes that may need to be pushed later
      this._hasActivitySinceLastPush = true;

      console.log('📝 [AUTO-COMMIT] Cell execution detected - auto-commit will be triggered after next save');
      console.log('💾 [AUTO-COMMIT] Avoiding manual save to prevent hash mismatch popup');
      console.log('⏰ [AUTO-COMMIT] JupyterLab will automatically save due to execution count change');
      console.log('🔄 [AUTO-COMMIT] Pending auto-commit stored, waiting for natural save cycle');

      // Add fallback timeout in case JupyterLab doesn't auto-save
      const fallbackTimeoutMs = 1000; // 1 second timeout
      this._autoCommitTimeout = setTimeout(async () => {
        console.log('⏰ [AUTO-COMMIT-FALLBACK] Natural save timeout reached, forcing save...');

        if (this._pendingAutoCommit && this._autoOperationsEnabled) {
          console.log('🚨 [AUTO-COMMIT-FALLBACK] JupyterLab did not auto-save after cell execution');
          console.log('💾 [AUTO-COMMIT-FALLBACK] Triggering manual save with hash mismatch auto-dismissal');

          try {
            // The hash mismatch auto-dismissal is already set up, so we can safely trigger a manual save
            await this._notebookPanel.context.save();
            console.log('✅ [AUTO-COMMIT-FALLBACK] Manual save completed - auto-commit should trigger now');
          } catch (error) {
            console.error('❌ [AUTO-COMMIT-FALLBACK] Manual save failed:', error);
            // Execute auto-commit directly if save fails
            console.log('🔄 [AUTO-COMMIT-FALLBACK] Save failed, executing auto-commit directly...');
            await this._executeDirectAutoCommit();
          }
        } else {
          console.log('⏭️ [AUTO-COMMIT-FALLBACK] No pending auto-commit or auto-operations disabled');
        }

        this._autoCommitTimeout = null;
      }, fallbackTimeoutMs);

      console.log(`⏱️ [AUTO-COMMIT] Fallback timeout set for ${fallbackTimeoutMs}ms in case natural save doesn't occur`);

    } catch (error) {
      console.error('💥 [AUTO-COMMIT] Unexpected error during auto-commit sequence:', error);
      console.error('🔧 [AUTO-COMMIT] This indicates a client-side error or network failure');
      // Silently fail to avoid disrupting user workflow
    }
  }

  /**
   * Execute auto-commit directly without waiting for save (fallback method).
   */
  private async _executeDirectAutoCommit(): Promise<void> {
    if (!this._pendingAutoCommit) {
      console.log('⏭️ [DIRECT-AUTO-COMMIT] No pending auto-commit to execute');
      return;
    }

    console.log('🚀 [DIRECT-AUTO-COMMIT] Executing auto-commit directly...');

    try {
      const notebookPath = getAbsoluteNotebookPathSync(this._notebookPanel.context.path);
      const currentNotebookContent = this._notebookPanel.content.model?.toJSON();

      if (!currentNotebookContent) {
        console.error('❌ [DIRECT-AUTO-COMMIT] Could not get current notebook content');
        return;
      }

      // Perform auto-commit with content
      const commitResult = await gitLockSignAPI.autoCommitWithContent(
        notebookPath,
        currentNotebookContent,
        this._pendingAutoCommit.cellPreview,
        this._pendingAutoCommit.executionCount
      );

      if (commitResult.success) {
        if (commitResult.debounced) {
          console.log(`⏱️ [DIRECT-AUTO-COMMIT] Auto-commit debounced - will execute in ${this._commitDebounceSeconds} seconds`);
        } else {
          console.log('✅ [DIRECT-AUTO-COMMIT] Auto-commit completed successfully');
          if (commitResult.commit_hash) {
            console.log('🔗 [DIRECT-AUTO-COMMIT] Commit hash:', commitResult.commit_hash);
          }
          this._showNotification('Auto-commit: Cell execution tracked (fallback)', 'success');
        }
      } else {
        console.error('❌ [DIRECT-AUTO-COMMIT] Auto-commit failed:', commitResult.error);
      }

      // Clear the pending auto-commit
      this._pendingAutoCommit = null;

    } catch (error) {
      console.error('❌ [DIRECT-AUTO-COMMIT] Error during direct auto-commit:', error);
    }
  }

  /**
   * Reload the notebook from disk to sync with backend changes.
   * This prevents file change conflict dialogs after auto-commits.
   */
  // private async _reloadNotebook(): Promise<void> {
  //   try {
  //     console.log('🔄 [NotebookLockManager] STARTING notebook reload to sync with auto-commit changes...');
  //     console.log('🔄 [NotebookLockManager] Notebook path:', this._notebookPanel.context.path);

  //     // Try multiple reload approaches
  //     try {
  //       // Method 1: Use context.revert() to reload from disk
  //       console.log('🔄 [NotebookLockManager] Attempting context.revert()...');
  //       await this._notebookPanel.context.revert();
  //       console.log('✅ [NotebookLockManager] context.revert() completed successfully');
  //     } catch (revertError) {
  //       console.warn('⚠️ [NotebookLockManager] context.revert() failed, trying alternative method:', revertError);

  //       // Method 2: Try context.reload() if available
  //       if ('reload' in this._notebookPanel.context && typeof this._notebookPanel.context.reload === 'function') {
  //         console.log('🔄 [NotebookLockManager] Attempting context.reload()...');
  //         await (this._notebookPanel.context as any).reload();
  //         console.log('✅ [NotebookLockManager] context.reload() completed successfully');
  //       } else {
  //         console.warn('⚠️ [NotebookLockManager] context.reload() not available');
  //         throw revertError;
  //       }
  //     }

  //     console.log('✅ [NotebookLockManager] Notebook reloaded successfully - should prevent file change conflicts');
  //   } catch (error) {
  //     console.error('❌ [NotebookLockManager] Failed to reload notebook after auto-commit:', error);
  //     console.log('ℹ️ [NotebookLockManager] You may see a "file has changed" popup - this is expected if reload failed');
  //     // Don't throw error - the auto-commit was successful, reload is just for UX
  //   }
  // }

  /**
   * Handle notebook save completion - trigger auto-commit if pending.
   * Auto-push only happens for manual saves or scheduled timer events.
   */
  private async _handleNotebookSaveCompleted(): Promise<void> {
    if (!this._autoOperationsEnabled) {
      console.log('⏸️ [AUTO-OPERATIONS] Auto-operations disabled, skipping auto-operations');
      return;
    }

    // Check if file deletion auto-push is already in progress to avoid duplicates
    if (this._fileLifecycleTracker?.isDeletionPushInProgress?.(this._notebookPanel.context.path)) {
      console.log('🚫 [AUTO-OPERATIONS] File deletion auto-push already in progress, skipping duplicate operations');
      return;
    }

    if (this._saveInProgress) {
      console.log('⚠️ [AUTO-OPERATIONS] Save still in progress, deferring auto-operations');
      return;
    }

    if (this._autoOperationInProgress) {
      console.log('⚠️ [AUTO-OPERATIONS] Auto-operation already in progress, skipping to prevent conflicts');
      return;
    }

    // Clear any pending auto-commit timeout since natural save occurred
    if (this._autoCommitTimeout) {
      console.log('✅ [AUTO-COMMIT] Natural save occurred, clearing fallback timeout');
      clearTimeout(this._autoCommitTimeout);
      this._autoCommitTimeout = null;
    }

    console.log('🚀 [AUTO-OPERATIONS] Starting auto-operation sequence...');

    // Create a promise to track this operation
    const operationPromise = (async () => {
      try {
        const notebookPath = getAbsoluteNotebookPathSync(this._notebookPanel.context.path);

        // Check if we have a pending auto-commit from cell execution
        if (this._pendingAutoCommit) {
          console.log('🚀 [AUTO-COMMIT] Executing pending auto-commit from cell execution...');
          console.log('📂 [AUTO-COMMIT] Notebook path:', notebookPath);
          console.log(`📝 [AUTO-COMMIT] Cell preview: "${this._pendingAutoCommit.cellPreview}"`);
          console.log(`🔢 [AUTO-COMMIT] Execution count: ${this._pendingAutoCommit.executionCount}`);

        try {
          // Get the current notebook content from memory (now saved to disk)
          const currentNotebookContent = this._notebookPanel.content.model?.toJSON();
          if (!currentNotebookContent) {
            console.error('❌ [AUTO-COMMIT] Could not get current notebook content for auto-commit');
          } else {
            // Perform auto-commit with content
            const commitResult = await gitLockSignAPI.autoCommitWithContent(
              notebookPath,
              currentNotebookContent,
              this._pendingAutoCommit.cellPreview,
              this._pendingAutoCommit.executionCount
            );

            if (commitResult.success) {
              if (commitResult.debounced) {
                console.log(`⏱️ [AUTO-COMMIT] Auto-commit debounced - will execute in ${this._commitDebounceSeconds} seconds`);
              } else {
                console.log('✅ [AUTO-COMMIT] Auto-commit completed successfully');
                if (commitResult.commit_hash) {
                  console.log('🔗 [AUTO-COMMIT] Commit hash:', commitResult.commit_hash);
                }
                this._showNotification('Auto-commit: Cell execution tracked', 'success');
              }
            } else {
              console.error('❌ [AUTO-COMMIT] Auto-commit failed:', commitResult.error);
            }
          }
        } catch (commitError) {
          console.error('❌ [AUTO-COMMIT] Error during auto-commit:', commitError);
        }

        // Clear the pending auto-commit
        this._pendingAutoCommit = null;
      }

      // NOTE: Auto-push is now decoupled from auto-commit to allow different frequencies
      // Auto-commit happens after cell execution, auto-push only happens on:
      // 1. Manual saves (File -> Save or Ctrl+S)
      // 2. Scheduled timer based on AUTO_SAVE_INTERVAL_MINUTES
      console.log('💾 [AUTO-OPERATIONS] Auto-commit completed, checking if auto-push is needed...');

      // Only trigger auto-push if this was a manual save
      if (this._isManualSave) {
        console.log('📝 [AUTO-PUSH] Triggering auto-push due to manual save');
        console.log('📂 [AUTO-PUSH] Notebook path:', notebookPath);
        console.log('💾 [AUTO-PUSH] Step 1: Backend will check for uncommitted changes and auto-commit if needed');
        console.log('🔍 [AUTO-PUSH] Step 2: Backend will check for unpushed commits from other files');
        console.log('📝 [AUTO-PUSH] Step 3: If other commits found, they will be pushed first (pre-commit auto-push)');
        console.log('⚡ [AUTO-PUSH] Step 4: Then current notebook changes (including any new auto-commit) will be pushed');

        const result = await gitLockSignAPI.autoPush(notebookPath);

        if (result.success) {
          if (result.debounced) {
            console.log(`⏱️ [AUTO-PUSH] Auto-push debounced - will execute in ${this._pushDebounceSeconds} seconds`);
            console.log('🔄 [AUTO-PUSH] Debouncing prevents spam pushes and batches multiple changes');
            console.log('💾 [AUTO-PUSH] Auto-commit before push will still be performed when debounce executes');
          } else {
            console.log('✅ [AUTO-PUSH] Enhanced auto-push sequence completed successfully');
            console.log('📦 [AUTO-PUSH] All changes (including any unsaved changes) have been captured and pushed');

            // NOTE: Removed notebook reload after auto-push to prevent file modifications
            // The reload was causing the file to appear modified again in git status
            // since context.revert() writes to disk after we've already committed and pushed
            console.log('✅ [AUTO-PUSH] Auto-push completed - no reload needed since changes are already captured');

            // Reset activity flag since we just pushed all changes
            this._hasActivitySinceLastPush = false;

            this._showNotification('Auto-push: All changes synchronized', 'success');
            console.log('🎉 [AUTO-PUSH] Auto-push completed successfully');
          }
        } else {
          console.error('❌ [AUTO-PUSH] Enhanced auto-push sequence failed:', result.error);
          console.error('🔧 [AUTO-PUSH] This could be due to:');
          console.error('   - Network connectivity issues');
          console.error('   - Git repository access problems');
          console.error('   - Merge conflicts that require manual resolution');
          console.error('   - Authentication/authorization issues');
          console.error('   - Auto-commit issues (permissions, disk space, etc.)');
          // Don't show error notification to avoid disrupting user workflow
        }

        // Reset the manual save flag after processing
        this._isManualSave = false;

        // Clear countdown since manual push just happened, timer will reset
        if (this._autoPushCountdownInterval) {
          clearInterval(this._autoPushCountdownInterval);
          this._autoPushCountdownInterval = null;
        }
      } else {
        console.log('⏭️ [AUTO-PUSH] Skipping auto-push - not a manual save (JupyterLab auto-save)');
        console.log('📅 [AUTO-PUSH] Auto-push will occur on next manual save or scheduled timer');

        // Reset the manual save flag after processing
        this._isManualSave = false;
      }

      } catch (error) {
        console.error('💥 [AUTO-OPERATIONS] Error during auto-operations:', error);
      } finally {
        this._autoOperationInProgress = false;
        this._currentAutoOperation = null;
      }
    })();

    this._currentAutoOperation = operationPromise;
    this._autoOperationInProgress = true;
  }

  /**
   * Get a preview of the last executed cell content.
   */
  private _getLastExecutedCellPreview(cellIndex?: number, cellId?: string): string {
    try {
      const notebook = this._notebookPanel.content;
      if (!notebook) {
        return '';
      }

      const cells = notebook.widgets;

      // If specific cell info provided, use it
      if (cellId) {
        const targetCell = cells.find(c => c.model.id === cellId);
        if (targetCell && targetCell.model.type === 'code' && targetCell.model.sharedModel.source) {
          const source = targetCell.model.sharedModel.source;
          return source.substring(0, 50).replace(/\n/g, ' ').trim();
        }
      }

      // Fallback: Find the most recently executed cell (highest execution count)
      let lastExecutedCell = null;
      let maxExecutionCount = 0;

      for (const cell of cells) {
        if (cell.model.type === 'code') {
          const executionCount = (cell.model as any).executionCount;
          if (executionCount && executionCount > maxExecutionCount) {
            maxExecutionCount = executionCount;
            lastExecutedCell = cell;
          }
        }
      }

      if (lastExecutedCell && lastExecutedCell.model.sharedModel.source) {
        const source = lastExecutedCell.model.sharedModel.source;
        return source.substring(0, 50).replace(/\n/g, ' ').trim();
      }

      return '';

    } catch (error) {
      console.error('Error getting cell preview:', error);
      return '';
    }
  }

  /**
   * Show a notification to the user.
   */
  private _showNotification(message: string, type: 'success' | 'error'): void {
    try {
      this.notificationSignal.emit({ msg: message, type });
    } catch (error) {
      console.error('Error showing notification:', error);
    }
  }

  /**
   * Handle notebook content changes.
   */
  private _onContentChanged(): void {
    // Mark activity when cell content is edited
    if (!this._isLocked) {  // Only track activity when notebook is not locked
      this._hasActivitySinceLastPush = true;
      console.log('📝 [CELL-EDIT] Cell content changed - marked activity for future auto-push scheduling');
    }

    // If notebook is locked and content changes, we might want to warn the user
    // For now, we'll just re-check the status
    if (this._isLocked) {
      console.warn('Content changed in locked notebook');
      // Optionally re-check status or show warning
    }
  }

  /**
   * Handle notebook model changes.
   */
  private _onModelChanged(): void {
    // Re-apply cell locking to any new cells
    if (this._isLocked) {
      console.log('📝 Model changed - applying enhanced locking to new cells...');

      // Use a small delay to ensure new cells are fully initialized
      setTimeout(() => {
        this._applyCellLocking(true);
      }, 50);
    }
  }

  /**
   * Check initial lock status when manager is created.
   */
  private async _checkInitialStatus(): Promise<void> {
    // Wait for notebook to fully load before checking status
    console.log('🚀 Enhanced initial status check - waiting 500ms for full initialization...');

    // Wait a bit for notebook to fully initialize
    await new Promise(resolve => setTimeout(resolve, 500));

    // Check status based on actual notebook metadata
    console.log('🔍 Checking status based on actual notebook metadata...');
    await this.checkStatus();

    // If locked, ensure cells are actually read-only
    if (this._isLocked) {
      console.log('🔍 Applying read-only enforcement based on metadata...');
      this._applyCellLocking(true);

      // Double-check after a short delay to handle any race conditions
      setTimeout(() => {
        if (this._isLocked) {
          console.log('🔄 Re-applying cell locking for safety (enhanced version)...');
          this._applyCellLocking(true);
        }
      }, 200);
    } else {
      console.log('✅ Notebook is not locked - no read-only enforcement needed');
    }
  }

  /**
   * Apply or remove locking to all cells in the notebook.
   */
  private _applyCellLocking(locked: boolean): void {
    if (!this._notebookPanel.content) {
      return;
    }

    const notebook = this._notebookPanel.content;
    const cells = notebook.widgets;

    cells.forEach((cell: Cell) => {
      this._applyCellLockState(cell, locked);
    });

    // Also disable/enable notebook operations
    this._disableNotebookOperations(locked);

    // Also disable/enable individual cell action buttons
    this._disableCellActionButtons(locked);
  }

  /**
   * Apply lock state to a single cell.
   */
  private _applyCellLockState(cell: Cell, locked: boolean): void {
    console.log(`🔐 Applying multi-layer read-only enforcement to cell (locked: ${locked})`);

    if (locked) {
      // Multiple approaches to ensure read-only state
      cell.node.classList.add('git-lock-sign-locked');
      cell.readOnly = true;
      console.log('🔒 Setting cell.readOnly = true and adding CSS class');

      // Disable input areas directly for stronger enforcement
      const inputAreas = cell.node.querySelectorAll('.jp-InputArea-editor');
      console.log(`🔒 Setting contenteditable=false on ${inputAreas.length} input areas`);
      inputAreas.forEach(area => {
        const element = area as HTMLElement;
        element.setAttribute('contenteditable', 'false');
        element.style.pointerEvents = 'none';
        element.style.userSelect = 'none';
        element.style.cursor = 'not-allowed';
      });

      // Disable CodeMirror editors if present
      const codeMirrorElements = cell.node.querySelectorAll('.CodeMirror');
      console.log(`🚫 Disabling ${codeMirrorElements.length} CodeMirror editors with pointer-events: none`);
      codeMirrorElements.forEach(cm => {
        const element = cm as HTMLElement;
        element.style.pointerEvents = 'none';
        element.style.cursor = 'not-allowed';

        // Hide cursor
        const cursors = element.querySelectorAll('.CodeMirror-cursor');
        cursors.forEach(cursor => {
          (cursor as HTMLElement).style.display = 'none';
        });
      });
      console.log('👁️ Hiding CodeMirror cursors for read-only enforcement');

      // Disable any input elements
      const inputs = cell.node.querySelectorAll('input, textarea');
      console.log(`🔒 Disabling ${inputs.length} input/textarea elements`);
      inputs.forEach(input => {
        (input as HTMLInputElement).disabled = true;
      });

      console.log(`✅ Cell locked - readOnly: ${cell.readOnly}, class added: ${cell.node.classList.contains('git-lock-sign-locked')}`);
    } else {
      // Remove locked styling and make editable
      cell.node.classList.remove('git-lock-sign-locked');
      cell.readOnly = false;
      console.log('🔓 Removing cell.readOnly and CSS class');

      // Re-enable input areas
      const inputAreas = cell.node.querySelectorAll('.jp-InputArea-editor');
      console.log(`🔓 Re-enabling ${inputAreas.length} input areas`);
      inputAreas.forEach(area => {
        const element = area as HTMLElement;
        element.removeAttribute('contenteditable');
        element.style.pointerEvents = '';
        element.style.userSelect = '';
        element.style.cursor = '';
      });

      // Re-enable CodeMirror editors
      const codeMirrorElements = cell.node.querySelectorAll('.CodeMirror');
      console.log(`✅ Re-enabling ${codeMirrorElements.length} CodeMirror editors`);
      codeMirrorElements.forEach(cm => {
        const element = cm as HTMLElement;
        element.style.pointerEvents = '';
        element.style.cursor = '';

        // Show cursor
        const cursors = element.querySelectorAll('.CodeMirror-cursor');
        cursors.forEach(cursor => {
          (cursor as HTMLElement).style.display = '';
        });
      });

      // Re-enable input elements
      const inputs = cell.node.querySelectorAll('input, textarea');
      console.log(`✅ Re-enabling ${inputs.length} input/textarea elements`);
      inputs.forEach(input => {
        (input as HTMLInputElement).disabled = false;
      });

      console.log(`✅ Cell unlocked - readOnly: ${cell.readOnly}, class removed: ${!cell.node.classList.contains('git-lock-sign-locked')}`);
    }
  }


  /**
   * Set up keyboard override system to disable shortcuts when locked.
   */
  private _setupKeyboardOverrides(): void {
    // Add event listener to capture keyboard events before JupyterLab processes them
    document.addEventListener('keydown', this._handleKeyDown, true);
    console.log('🎹 Keyboard override system initialized');
  }

  /**
   * Handle keydown events to block disabled shortcuts when notebook is locked.
   */
  private _handleKeyDown = (event: KeyboardEvent): void => {
    // Only intercept if this notebook is locked and focused
    if (!this._isLocked || this._isDisposed) {
      return;
    }

    // Check if the event is targeting this notebook
    if (!this._isEventTargetingThisNotebook(event)) {
      return;
    }

    // Check if this is a disabled shortcut
    const disabledShortcut = this._findDisabledShortcut(event);
    if (disabledShortcut) {
      console.log(`🚫 Blocking disabled shortcut: ${disabledShortcut.description}`);
      event.preventDefault();
      event.stopPropagation();
      event.stopImmediatePropagation();

      // Show user feedback
      this._showShortcutBlockedMessage(disabledShortcut.description);
      return;
    }

    // Special handling for double-key shortcuts (DD for delete, 00 for restart)
    this._handleDoubleKeyShortcuts(event);
  };

  /**
   * Check if the keyboard event is targeting this notebook.
   */
  private _isEventTargetingThisNotebook(event: KeyboardEvent): boolean {
    const target = event.target as HTMLElement;
    if (!target) return false;

    // Check if the event target is within this notebook panel
    return this._notebookPanel.node.contains(target);
  }

  /**
   * Find if the current key combination matches a disabled shortcut.
   */
  private _findDisabledShortcut(event: KeyboardEvent): any {
    return this._disabledShortcuts.find(shortcut => {
      return (
        shortcut.key.toLowerCase() === event.key.toLowerCase() &&
        shortcut.ctrlKey === event.ctrlKey &&
        shortcut.shiftKey === event.shiftKey &&
        shortcut.altKey === event.altKey
      );
    });
  }

  /**
   * Handle double-key shortcuts like DD (delete) and 00 (restart kernel).
   */
  private _handleDoubleKeyShortcuts(event: KeyboardEvent): void {
    // This is a simplified implementation - in a full implementation,
    // you'd need to track the timing and sequence of key presses
    if (event.key === 'd' || event.key === '0') {
      // For now, just block these keys entirely when locked
      console.log(`🚫 Blocking potential double-key shortcut: ${event.key}`);
      event.preventDefault();
      event.stopPropagation();
      this._showShortcutBlockedMessage(`Key '${event.key}' (potential double-key shortcut)`);
    }
  }

  /**
   * Show a message to the user when a shortcut is blocked.
   */
  private _showShortcutBlockedMessage(shortcutDescription: string): void {
    // Create a temporary notification
    const notification = document.createElement('div');
    notification.className = 'git-lock-sign-shortcut-blocked';
    notification.innerHTML = `🔒 Shortcut blocked: ${shortcutDescription}`;
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: var(--jp-warn-color3);
      border: 1px solid var(--jp-warn-color1);
      border-radius: 4px;
      padding: 8px 12px;
      z-index: 10000;
      font-size: 12px;
      color: var(--jp-warn-color0);
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    `;

    document.body.appendChild(notification);

    // Remove after 2 seconds
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 2000);
  }

  /**
   * Disable notebook toolbar buttons when locked.
   */
  private _disableNotebookOperations(disabled: boolean): void {
    if (!this._notebookPanel.content) {
      return;
    }

    console.log(`${disabled ? '🚫' : '✅'} ${disabled ? 'Disabling' : 'Enabling'} notebook operations...`);

    // Disable toolbar buttons by finding them in the DOM
    const toolbarNode = this._notebookPanel.toolbar.node;
    const toolbarButtons = toolbarNode.querySelectorAll('button, .jp-ToolbarButton');

    toolbarButtons.forEach(button => {
      const buttonElement = button as HTMLElement;
      const title = buttonElement.title || buttonElement.getAttribute('data-command') || '';

      // Check if this is a button we want to disable
      const shouldDisable = title.toLowerCase().includes('insert') ||
                           title.toLowerCase().includes('cut') ||
                           title.toLowerCase().includes('copy') ||
                           title.toLowerCase().includes('paste') ||
                           title.toLowerCase().includes('delete') ||
                           buttonElement.className.includes('insert') ||
                           buttonElement.className.includes('cut') ||
                           buttonElement.className.includes('copy') ||
                           buttonElement.className.includes('paste');

      if (shouldDisable) {
        if (disabled) {
          buttonElement.style.opacity = '0.5';
          buttonElement.style.pointerEvents = 'none';
          buttonElement.setAttribute('data-original-title', buttonElement.title);
          buttonElement.title = 'Disabled - notebook is locked';
        } else {
          buttonElement.style.opacity = '';
          buttonElement.style.pointerEvents = '';
          const originalTitle = buttonElement.getAttribute('data-original-title');
          if (originalTitle) {
            buttonElement.title = originalTitle;
            buttonElement.removeAttribute('data-original-title');
          }
        }
      }
    });

    // Disable context menus on cells
    const cells = this._notebookPanel.content.widgets;
    cells.forEach(cell => {
      if (disabled) {
        cell.node.addEventListener('contextmenu', this._blockContextMenu, true);
      } else {
        cell.node.removeEventListener('contextmenu', this._blockContextMenu, true);
      }
    });
  }

  /**
   * Block context menu events on locked cells.
   */
  private _blockContextMenu = (event: MouseEvent): void => {
    if (this._isLocked) {
      event.preventDefault();
      event.stopPropagation();
      this._showShortcutBlockedMessage('Context menu');
    }
  };

  /**
   * Disable notebook actions when locked - expanded to cover entire notebook including "Click to add cell" area.
   */
  private _disableCellActionButtons(disabled: boolean): void {
    if (!this._notebookPanel.content) {
      return;
    }

    console.log(`${disabled ? '🚫' : '✅'} ${disabled ? 'Blocking' : 'Unblocking'} notebook actions...`);

    if (disabled) {
      // Block clicks on the entire notebook container to catch "Click to add cell" area
      this._notebookPanel.content.node.addEventListener('click', this._blockNotebookClicks, true);
      console.log('🚫 Added click blocker to entire notebook container');
    } else {
      // Remove notebook-level click blocker
      this._notebookPanel.content.node.removeEventListener('click', this._blockNotebookClicks, true);
      console.log('✅ Removed click blocker from notebook container');
    }
  }

  /**
   * Block all interactive actions within the notebook when locked - including "Click to add cell" area.
   */
  private _blockNotebookClicks = (event: MouseEvent): void => {
    if (!this._isLocked) {
      return;
    }

    const target = event.target as HTMLElement;
    if (!target) {
      return;
    }

    // Check for various types of interactive elements
    const isBlockableAction =
      // Regular buttons and toolbars
      target.closest('button') ||
      target.closest('.jp-ToolbarButton') ||
      target.closest('.jp-Button') ||
      target.closest('[role="button"]') ||
      target.closest('.jp-Cell-toolbar') ||
      target.closest('[data-command]') ||

      // "Click to add cell" area and related elements
      target.closest('.jp-Notebook-footer') ||
      target.closest('.jp-Notebook-addCellButton') ||
      target.classList.contains('jp-Notebook-footer') ||
      target.classList.contains('jp-Notebook-addCellButton') ||

      // Check for add-cell functionality by attributes
      (target.getAttribute('title') && target.getAttribute('title')!.toLowerCase().includes('add')) ||
      (target.getAttribute('aria-label') && target.getAttribute('aria-label')!.toLowerCase().includes('add')) ||

      // Check for click-to-add areas by class patterns
      target.className.includes('add') ||
      target.className.includes('Add') ||

      // Check parent elements for add-cell functionality
      target.parentElement?.className.includes('add') ||
      target.parentElement?.getAttribute('title')?.toLowerCase().includes('add');

    if (isBlockableAction) {
      console.log('🚫 Blocking notebook action click:', {
        className: target.className,
        title: target.title,
        ariaLabel: target.getAttribute('aria-label'),
        tagName: target.tagName
      });
      event.preventDefault();
      event.stopPropagation();
      event.stopImmediatePropagation();
      this._showShortcutBlockedMessage('Notebook action blocked');
    }
  };

}
