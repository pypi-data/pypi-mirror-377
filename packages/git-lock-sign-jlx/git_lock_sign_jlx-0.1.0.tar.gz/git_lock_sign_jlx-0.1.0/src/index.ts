import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { INotebookTracker } from '@jupyterlab/notebook';
import { IToolbarWidgetRegistry } from '@jupyterlab/apputils';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import { NotebookPanel, INotebookModel } from '@jupyterlab/notebook';
import { IDisposable, DisposableDelegate } from '@lumino/disposable';
import { ReactWidget } from '@jupyterlab/apputils';
import * as React from 'react';
import { PushButtonComponent } from './components/PushButton';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { ServiceManager } from '@jupyterlab/services';
import { IDefaultFileBrowser } from '@jupyterlab/filebrowser';

import { LockButtonWidget } from './components/LockButton';
import { CommitButtonWidget } from './components/CommitButton';
import { NotebookLockManager } from './components/NotebookLockManager';
import { UserInfoDisplayWidget } from './components/UserInfoDisplay';
import { NotebookLockIndicatorWidget } from './components/NotebookLockIndicator';
import { stripRTCPrefix, getAbsoluteNotebookPath, gitLockSignAPI } from './services/api';
import '../style/commit-button.css';

/**
 * Global file lifecycle tracker for auto-commits on creation/deletion.
 */
class FileLifecycleTracker implements IDisposable {
  private _docManager: IDocumentManager;
  private _serviceManager: ServiceManager.IManager;
  private _isDisposed: boolean = false;
  private _trackingActive: boolean = false;
  private _deletionPushTracker: Set<string> = new Set();
  private _enableFileCreationTracking: boolean = false;
  private _fileRenameTracker: Map<string, { oldPath: string; timestamp: number }> = new Map();
  private _renameDetectionTimeout: number = 3000; // 3 second timeout for rename detection

  constructor(docManager: IDocumentManager, serviceManager: ServiceManager.IManager) {
    try {
      this._docManager = docManager;
      this._serviceManager = serviceManager;
      // Initialize configuration and setup tracking asynchronously
      this._initializeAsync();
    } catch (error) {
      console.error('❌ FileLifecycleTracker initialization failed:', error);
      throw error;
    }
  }

  private async _initializeAsync(): Promise<void> {
    await this._initializeConfiguration();
    this._setupFileTracking();
  }

  get isDisposed(): boolean {
    return this._isDisposed;
  }

  dispose(): void {
    if (this._isDisposed) {
      return;
    }
    this._isDisposed = true;
    this._trackingActive = false;
    
    // Clean up rename tracker
    this._fileRenameTracker.clear();
  }

  private async _initializeConfiguration(): Promise<void> {
    try {
      const config = await gitLockSignAPI.getConfig();
      if (config.success && config.enable_file_creation_tracking !== undefined) {
        this._enableFileCreationTracking = config.enable_file_creation_tracking;
      } else {
        this._enableFileCreationTracking = false;
      }
    } catch (error) {
      console.warn('⚠️ Failed to fetch file creation tracking config, defaulting to false');
      this._enableFileCreationTracking = false;
    }
  }

  private _setupFileTracking(): void {
    try {
      // Try both approaches: contents manager overrides AND document manager signals
      this._setupContentsManagerTracking();
      this._setupDocumentManagerSignals();
      
      this._trackingActive = true;
      console.log('✅ File lifecycle tracking setup complete');
    } catch (error) {
      console.error('❌ File lifecycle tracking setup failed:', error);
    }
  }

  private _setupContentsManagerTracking(): void {
    // Monitor file creation/deletion using the contents manager
    const contentsManager = this._serviceManager.contents;
    
    // Override the delete method to track deletions
    const originalDelete = contentsManager.delete.bind(contentsManager);
    contentsManager.delete = async (path: string) => {
      // Check if this is a notebook file
      if (path.endsWith('.ipynb')) {
        // Check if this might be a rename operation
        const renameInfo = this._fileRenameTracker.get(path);
        if (renameInfo) {
          // Don't trigger delete commit yet - wait for the new file to appear
          this._fileRenameTracker.delete(path);
        } else {
          // Add to rename tracker to detect potential renames
          this._fileRenameTracker.set(path, { oldPath: path, timestamp: Date.now() });
          
          // IMMEDIATELY record that we're processing this deletion to avoid duplicate auto-push
          // This prevents auto-push on close from interfering while we wait for rename detection
          this._deletionPushTracker.add(path);
          
          // Set a timeout to clean up if no rename is detected
          setTimeout(() => {
            if (this._fileRenameTracker.has(path)) {
              this._fileRenameTracker.delete(path);
              
              // Trigger lifecycle commit for deletion (with auto-push)
              this._triggerLifecycleCommit(path, 'delete', true);
              
              // Clean up tracking after some delay (to prevent any race conditions)
              setTimeout(() => {
                this._deletionPushTracker.delete(path);
              }, 5000);
            } else {
              // If rename was detected, clean up the deletion tracking since it's not a real deletion
              this._deletionPushTracker.delete(path);
            }
          }, this._renameDetectionTimeout);
          
          // Perform the actual deletion
          const result = await originalDelete(path);
          return result;
        }
      }
      
      // For non-notebook files, just perform normal deletion
      return originalDelete(path);
    };

    // Monitor file creation through directory listing changes and contents manager
    const originalSave = contentsManager.save.bind(contentsManager);
    contentsManager.save = async (path: string, options: any) => {
      // ✨ STRIP RTC PREFIX FROM PATH BEFORE SAVING TO DISK
      const cleanPath = stripRTCPrefix(path);
      
      // Also check file existence as backup (using clean path)
      const fileExists = await this._fileExists(cleanPath);
      
      // PRIMARY: Use file existence as the main indicator for new file creation
      // This handles cases where user executed cells before saving (content-based detection would fail)
      const isNewNotebook = cleanPath.endsWith('.ipynb') && 
                            options.type === 'notebook' && 
                            !fileExists;
      
      // ✨ SAVE WITH CLEAN PATH - THIS IS THE KEY CHANGE!
      const result = await originalSave(cleanPath, options);
      
      // Check if this might be a rename operation
      const renameInfo = this._detectRename(cleanPath, options);
      
      if (renameInfo) {
        // Trigger rename commit with auto-push (like deletions)
        await this._triggerLifecycleCommit(cleanPath, 'rename', true, renameInfo.oldPath);
      } else if (isNewNotebook) {
        // Check if file creation tracking is enabled before triggering commit
        if (this._enableFileCreationTracking) {
          await this._triggerLifecycleCommit(cleanPath, 'create', false);
        }
      }
      
      return result;
    };
    
  }

  private _setupDocumentManagerSignals(): void {
    // Listen to document manager signals for file operations
    if (this._docManager && this._docManager.services && this._docManager.services.contents) {
      const contents = this._docManager.services.contents;
      
      // Listen for file creation through fileChanged signal
      contents.fileChanged.connect((sender, change) => {
        if (change.type === 'rename' && change.oldValue && change.newValue && 
            change.oldValue.path && change.newValue.path && 
            change.oldValue.path.endsWith('.ipynb') && change.newValue.path.endsWith('.ipynb')) {
          // Handle rename through document manager signal
          this._handleRenameEvent(change.oldValue.path, change.newValue.path);
        }
      });
    }
  }

  private async _fileExists(path: string): Promise<boolean> {
    try {
      await this._serviceManager.contents.get(path);
      return true;
    } catch {
      return false;
    }
  }

  private _detectRename(newPath: string, options: any): { oldPath: string } | null {
    // Check if we have a tracked deletion that might be a rename
    // Look for deletions that happened recently (within the rename detection timeout)
    const now = Date.now();
    
    for (const [deletedPath, info] of this._fileRenameTracker.entries()) {
      if (now - info.timestamp < this._renameDetectionTimeout) {
        // Check if the content matches (this is a simple heuristic)
        // In a real implementation, you might want to compare file contents
        if (this._isLikelyRename(deletedPath, newPath)) {
          this._fileRenameTracker.delete(deletedPath);
          return { oldPath: deletedPath };
        }
      } else {
        // Clean up old entries
        this._fileRenameTracker.delete(deletedPath);
      }
    }
    
    return null;
  }

  private _isLikelyRename(oldPath: string, newPath: string): boolean {
    // More flexible rename detection:
    // 1. Check if paths are in the same directory (most common case)
    // 2. Check if paths are in the same repository (different subdirectories)
    // 3. Check if the timing is very close (within a few seconds)
    
    const oldDir = oldPath.substring(0, oldPath.lastIndexOf('/'));
    const newDir = newPath.substring(0, newPath.lastIndexOf('/'));
    
    // If directories are the same, it's very likely a rename
    if (oldDir === newDir) {
      return true;
    }
    
    // If directories are different but in the same repository, it might still be a rename
    // This handles cases where files are moved between subdirectories
    if (oldDir && newDir && (oldDir.startsWith(newDir) || newDir.startsWith(oldDir))) {
      return true;
    }
    
    // For now, be conservative and only allow same-directory renames
    // You can make this more flexible by checking repository boundaries
    return false;
  }

  private async _handleRenameEvent(oldPath: string, newPath: string): Promise<void> {
    // Clean up any existing rename tracker entries for the old path
    if (this._fileRenameTracker.has(oldPath)) {
      this._fileRenameTracker.delete(oldPath);
    }
    
    // Trigger rename commit with auto-push
    await this._triggerLifecycleCommit(newPath, 'rename', true, oldPath);
  }

  private async _triggerLifecycleCommit(filePath: string, lifecycleEvent: 'create' | 'delete' | 'rename', triggerAutoPush: boolean, oldFilePath?: string): Promise<void> {
    if (!this._trackingActive) {
      return;
    }
    
    try {
      // Use the same path logic as other components for consistency
      const absolutePath = await getAbsoluteNotebookPath(filePath);
      
      // Prepare request body
      const requestBody: any = {
        file_path: absolutePath,
        lifecycle_event: lifecycleEvent,
        trigger_auto_push: triggerAutoPush
      };
      
      // Add old_file_path for rename events
      if (lifecycleEvent === 'rename' && oldFilePath) {
        const absoluteOldPath = await getAbsoluteNotebookPath(oldFilePath);
        requestBody.old_file_path = absoluteOldPath;
      }
      
      // Call the JupyterLab backend handler instead of sidecar directly
      const response = await gitLockSignAPI.commitFileLifecycle(requestBody);

      if (response.success) {
        console.log(`✅ ${lifecycleEvent} commit successful`);
      } else {
        console.error(`❌ ${lifecycleEvent} commit failed:`, response.error);
      }
    } catch (error) {
      console.error(`❌ ${lifecycleEvent} commit error:`, error);
    }
  }



  /**
   * Check if a file deletion auto-push is already in progress to avoid duplicates.
   */
  isDeletionPushInProgress(path: string): boolean {
    return this._deletionPushTracker.has(path);
  }

  /**
   * Get current rename tracker status for debugging.
   */
  getRenameTrackerStatus(): Array<[string, { oldPath: string; timestamp: number }]> {
    return Array.from(this._fileRenameTracker.entries());
  }

  /**
   * Get current tracking status for debugging.
   */
  getTrackingStatus(): { trackingActive: boolean; isDisposed: boolean } {
    return {
      trackingActive: this._trackingActive,
      isDisposed: this._isDisposed
    };
  }
}

/**
 * Extension that adds lock button to notebook toolbar.
 */
class GitLockSignExtension implements DocumentRegistry.IWidgetExtension<NotebookPanel, INotebookModel> {
  private _managers: Map<string, NotebookLockManager> = new Map();
  private _app: JupyterFrontEnd;
  private _fileLifecycleTracker: FileLifecycleTracker;

  constructor(app: JupyterFrontEnd, fileLifecycleTracker: FileLifecycleTracker) {
    this._app = app;
    this._fileLifecycleTracker = fileLifecycleTracker;
  }

  /**
   * Create a new extension for the notebook panel widget.
   */
  createNew(
    panel: NotebookPanel,
    context: DocumentRegistry.IContext<INotebookModel>
  ): IDisposable {
    // Create lock manager for this notebook with app instance for command tracking
    const manager = new NotebookLockManager(panel, this._app, this._fileLifecycleTracker);
    this._managers.set(context.path, manager);

    // Create user info display widget (includes refresh button)
    const userInfoDisplay = new UserInfoDisplayWidget(panel);

    // Create notebook lock indicator widget
    const lockIndicator = new NotebookLockIndicatorWidget();

    // Create commit button widget
    const commitButton = new CommitButtonWidget(panel);

    // Create push button widget
    const pushButton = ReactWidget.create(
      React.createElement(PushButtonComponent, { notebookPanel: panel, lockManager: manager })
    );

    // Create lock button widget with manager reference
    const lockButton = new LockButtonWidget(panel, undefined, manager);

    // Connect lock indicator to manager state changes
    manager.stateChanged.connect(() => {
      lockIndicator.updateStatus(manager.isLocked, manager.signatureMetadata);
    });

    // Add widgets to toolbar in the new layout:
    // [Git User: John Doe <john@example.com>] [🔄 Refresh] ... [🔒 Locked] [Commit] [Push] [Lock]
    panel.toolbar.insertItem(9, 'gitUserInfo', userInfoDisplay);
    panel.toolbar.insertItem(11, 'gitLockIndicator', lockIndicator);
    panel.toolbar.insertItem(12, 'gitCommit', commitButton);
    panel.toolbar.insertItem(13, 'gitPush', pushButton);
    panel.toolbar.insertItem(14, 'gitLockSign', lockButton);

    // Clean up when panel is disposed
    const disposable = new DisposableDelegate(() => {
      manager.dispose();
      this._managers.delete(context.path);
      userInfoDisplay.dispose();
      lockIndicator.dispose();
      commitButton.dispose();
      pushButton.dispose();
      lockButton.dispose();
    });

    return disposable;
  }

  /**
   * Get the lock manager for a specific notebook path.
   */
  getManager(path: string): NotebookLockManager | undefined {
    return this._managers.get(path);
  }
}

/**
 * Initialize workspace session with repository setup and sync.
 * Called when JupyterLab extension loads to ensure user workspace is ready.
 */
async function initializeWorkspaceSession(serviceManager: ServiceManager.IManager): Promise<any> {
  try {
    // Get the actual workspace root directory from JupyterLab
    let workspacePath: string;
    
    try {
      // Get the actual working directory from our backend API
      // This gives us the exact directory where JupyterLab server is running
      const data = await gitLockSignAPI.getWorkingDirectory();
      
      if (data.success && data.working_directory) {
        workspacePath = data.working_directory;
      } else {
        // Fallback - use current directory indicator
        workspacePath = '.';
      }
    } catch (error) {
      console.warn('⚠️ Could not determine workspace dynamically, using current directory fallback');
      workspacePath = '.';
    }

    // Call the session initialization API
    const result = await gitLockSignAPI.initializeSession(workspacePath);
    
    if (result.success) {
      console.log('✅ Workspace session initialized successfully');
    } else {
      console.warn('⚠️ Session initialization completed with warnings:', result.error);
    }
    
    return result;
    
  } catch (error) {
    console.error('❌ Workspace session initialization error:', error);
    throw error;
  }
}

/**
 * Initialization data for the git_lock_sign_jlx extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'git_lock_sign_jlx:plugin',
  description: 'Git-based notebook locking and signing extension.',
  autoStart: true,
  requires: [INotebookTracker, IDocumentManager, IDefaultFileBrowser],
  optional: [ISettingRegistry, IToolbarWidgetRegistry],
  activate: (
    app: JupyterFrontEnd,
    notebookTracker: INotebookTracker,
    docManager: IDocumentManager,
    fileBrowser: IDefaultFileBrowser,
    settingRegistry: ISettingRegistry | null,
    toolbarRegistry: IToolbarWidgetRegistry | null
  ) => {
    console.log('🚀 JupyterLab extension git_lock_sign_jlx is activated!');

    // Create the file lifecycle tracker
    const fileLifecycleTracker = new FileLifecycleTracker(docManager, app.serviceManager);

    // Initialize session with workspace-level setup and UI feedback
    
    // Import SessionManager dynamically to avoid import order issues
    import('./services/sessionManager').then(({ SessionManager }) => {
      const sessionManager = new SessionManager(app.serviceManager, fileBrowser);
      
      sessionManager.initializeSession()
        .then((result: any) => {
          if (result.success) {
            console.log('✅ Workspace session initialized successfully');
          } else {
            console.warn('⚠️ Workspace session initialization had issues:', result.error);
          }
        })
        .catch((error: any) => {
          console.error('❌ Failed to initialize workspace session:', error);
          // Don't prevent extension loading if session init fails
        });
    }).catch((error: any) => {
      console.error('❌ Failed to load SessionManager:', error);
      // Fallback to direct initialization without UI
      initializeWorkspaceSession(app.serviceManager)
        .then((result: any) => {
          if (result.success) {
            console.log('✅ Workspace session initialized successfully (fallback)');
          } else {
            console.warn('⚠️ Workspace session initialization had issues (fallback):', result.error);
          }
        })
        .catch((fallbackError: any) => {
          console.error('❌ Fallback session initialization also failed:', fallbackError);
        });
    });

    // Create the extension instance
    const extension = new GitLockSignExtension(app, fileLifecycleTracker);

    // Register the extension with the notebook widget factory
    app.docRegistry.addWidgetExtension('Notebook', extension);

    // Load settings if available
    if (settingRegistry) {
      settingRegistry
        .load(plugin.id)
        .then(settings => {
          console.log('git_lock_sign_jlx settings loaded:', settings.composite);
        })
        .catch(reason => {
          console.error('Failed to load settings for git_lock_sign_jlx.', reason);
        });
    }

    // Register toolbar widget if toolbar registry is available
    if (toolbarRegistry) {
      toolbarRegistry.addFactory(
        'Notebook',
        'gitLockSign',
        (panel: NotebookPanel) => new LockButtonWidget(panel, undefined, undefined)
      );
    }

    console.log('✅ Git Lock Sign extension initialized successfully');
  }
};

export default plugin;
