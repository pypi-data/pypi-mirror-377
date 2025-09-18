import { Widget } from '@lumino/widgets';
import { ServiceManager } from '@jupyterlab/services';
import { IDefaultFileBrowser } from '@jupyterlab/filebrowser';


/**
 * Session manager that handles workspace initialization with UI feedback.
 */
export class SessionManager {
  private _isInitializing: boolean = false;
  private _overlayWidget: Widget | null = null;
  private _serviceManager: ServiceManager.IManager;
  private _fileBrowser: IDefaultFileBrowser;

  constructor(serviceManager: ServiceManager.IManager, fileBrowser: IDefaultFileBrowser) {
    this._serviceManager = serviceManager;
    this._fileBrowser = fileBrowser;
  }

  /**
   * Show the session sync overlay.
   */
  private _showOverlay(message?: string): void {
    if (this._overlayWidget) {
      return; // Already showing
    }

    // Create overlay widget
    this._overlayWidget = new Widget();
    this._overlayWidget.addClass('session-sync-overlay-widget');
    this._overlayWidget.id = 'session-sync-overlay';

    // Add CSS animations to the document if they don't exist
    if (!document.querySelector('#session-sync-animations')) {
      const style = document.createElement('style');
      style.id = 'session-sync-animations';
      style.textContent = `
        @keyframes sessionSyncRotate {
          100% { transform: rotate(360deg); }
        }
        @keyframes sessionSyncDash {
          0% { stroke-dasharray: 1, 150; stroke-dashoffset: 0; }
          50% { stroke-dasharray: 90, 150; stroke-dashoffset: -35; }
          100% { stroke-dasharray: 90, 150; stroke-dashoffset: -124; }
        }
        @keyframes sessionSyncProgress {
          0% { transform: translateX(-100%); }
          50% { transform: translateX(0%); }
          100% { transform: translateX(100%); }
        }
      `;
      document.head.appendChild(style);
    }

    // Create overlay HTML structure with inline styles as fallback
    const overlayHTML = `
      <div class="session-sync-overlay" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 10000; display: flex; align-items: center; justify-content: center; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;">
        <div class="session-sync-backdrop" style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.6); backdrop-filter: blur(3px);"></div>
        <div class="session-sync-modal" style="position: relative; background: white; border: 1px solid #ddd; border-radius: 8px; padding: 32px; min-width: 400px; max-width: 500px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);">
          <div class="session-sync-content" style="text-align: center;">
            <div class="session-sync-spinner" style="margin-bottom: 24px; display: flex; justify-content: center;">
              <svg class="session-sync-spinner-svg" width="40" height="40" viewBox="0 0 50 50" style="animation: sessionSyncRotate 1.2s linear infinite;">
                <circle
                  class="session-sync-spinner-path"
                  cx="25" cy="25" r="20"
                  fill="none" stroke="#2196f3" stroke-width="3"
                  stroke-linecap="round" stroke-dasharray="31.416" stroke-dashoffset="31.416"
                  style="animation: sessionSyncDash 1.5s ease-in-out infinite;"
                />
              </svg>
            </div>
            <div class="session-sync-message">
              <h3 style="margin: 0 0 8px 0; font-size: 18px; font-weight: 600; color: #333;">Initializing Workspace</h3>
              <p class="session-sync-status" style="margin: 0 0 16px 0; font-size: 14px; color: #666; line-height: 1.4;">${message || "Syncing workspace with remote repository..."}</p>
              <div class="session-sync-details" style="display: flex; flex-direction: column; gap: 6px; margin-bottom: 20px;">
                <span style="font-size: 12px; color: #888; text-align: left; padding-left: 8px;">• Setting up git repository</span>
                <span style="font-size: 12px; color: #888; text-align: left; padding-left: 8px;">• Connecting to remote server</span>
                <span style="font-size: 12px; color: #888; text-align: left; padding-left: 8px;">• Syncing files from remote</span>
              </div>
            </div>
            <div class="session-sync-progress" style="margin-top: 20px;">
              <div class="session-sync-progress-bar" style="width: 100%; height: 4px; background: #eee; border-radius: 2px; overflow: hidden;">
                <div class="session-sync-progress-fill" style="height: 100%; background: linear-gradient(90deg, #2196f3 0%, #1976d2 100%); border-radius: 2px; animation: sessionSyncProgress 2s ease-in-out infinite;"></div>
              </div>
            </div>
            

          </div>
        </div>
      </div>
    `;

    // Set the HTML content
    this._overlayWidget.node.innerHTML = overlayHTML;

    // Add to document body
    Widget.attach(this._overlayWidget, document.body);
  }

  /**
   * Hide the session sync overlay.
   */
  private _hideOverlay(): void {
    if (this._overlayWidget) {
      // Remove widget
      Widget.detach(this._overlayWidget);
      this._overlayWidget.dispose();
      this._overlayWidget = null;
    }
  }

  /**
   * Update the overlay message.
   */
  private _updateOverlayMessage(message: string): void {
    if (this._overlayWidget) {
      const statusElement = this._overlayWidget.node.querySelector('.session-sync-status');
      if (statusElement) {
        statusElement.textContent = message;
      }
    }
  }

  /**
   * Initialize workspace session with UI feedback.
   */
  async initializeSession(): Promise<{ success: boolean; message?: string; error?: string }> {
    if (this._isInitializing) {
      return { success: false, error: 'Session initialization already in progress' };
    }

    this._isInitializing = true;
    
    try {
      // Show overlay
      this._showOverlay("Initializing workspace session...");

      // Step 1: Get workspace path
      this._updateOverlayMessage("Determining workspace directory...");
      await this._delay(500); // Give users a moment to see the message
      
      let workspacePath: string;
      
      try {
        const { gitLockSignAPI } = await import('./api');
        const data = await gitLockSignAPI.getWorkingDirectory();
        
        if (data.success && data.working_directory) {
          workspacePath = data.working_directory;
        } else {
          workspacePath = '.';
        }
      } catch (error) {
        console.warn('⚠️ Could not determine workspace dynamically, using current directory fallback');
        workspacePath = '.';
      }

      // Step 2: Initialize session
      this._updateOverlayMessage("Setting up git repository and connecting to remote...");
      await this._delay(500);

      // Dynamic import to avoid circular dependencies
      const { gitLockSignAPI } = await import('./api');
      
      // Check if we should navigate to work subdirectory
      const shouldNavigateToWorkDir = await this._checkWorkSubdirectoryNavigation(workspacePath);
      
      // Start file browser refresh IMMEDIATELY when starting the sync
      this._refreshFileBrowser().catch(error => {
        // Immediate refresh failed
      });
      
      const result = await gitLockSignAPI.initializeSession(workspacePath);
      
      if (result.success) {
        this._updateOverlayMessage("Session initialization completed successfully!");
        await this._delay(1000);
        console.log('✅ Workspace session initialized successfully');
        
        // Navigate to work directory if enabled
        if (shouldNavigateToWorkDir) {
          this._updateOverlayMessage("Navigating to work directory...");
          await this._navigateToWorkDirectory(workspacePath);
          await this._delay(500);
        }
        
        // Refresh the file browser to show newly synced files immediately
        this._updateOverlayMessage("Refreshing file browser...");
        
        try {
          // Primary refresh attempt immediately
          await this._refreshFileBrowser();
          
          // Short pause then secondary refresh
          this._updateOverlayMessage("Ensuring files are visible...");
          await this._delay(800);
          
          // Secondary refresh with different timing
          await this._refreshFileBrowser();
          
          // Final success message with longer display
          this._updateOverlayMessage("Files updated successfully!");
          await this._delay(1200);
          
        } catch (error) {
          console.warn('⚠️ File browser refresh had issues:', error);
          this._updateOverlayMessage("Sync completed - refreshing files...");
          // Even if refresh failed, try one more time
          try {
            await this._refreshFileBrowser();
          } catch (finalError) {
            // Final refresh attempt failed
          }
          await this._delay(1000);
        }
      } else {
        this._updateOverlayMessage("Session initialization completed with warnings");
        await this._delay(1000);
        console.warn('⚠️ Session initialization completed with warnings:', result.error);
      }
      
      return result
      
    } catch (error) {
      this._updateOverlayMessage("Session initialization failed");
      await this._delay(1000);
      console.error('❌ Session initialization error:', error);
      return { success: false, error: `Session initialization failed: ${error}` };
    } finally {
      this._isInitializing = false;
      this._hideOverlay();
      
      // Continue refreshing the file browser in the background after overlay closes
      setTimeout(async () => {
        try {
          await this._refreshFileBrowser();
          
          // Try one more time after another delay
          setTimeout(async () => {
            try {
              await this._refreshFileBrowser();
            } catch (error) {
              // Final background refresh failed
            }
          }, 1000);
        } catch (error) {
          // Post-sync background refresh failed
        }
      }, 500);
    }
  }

  /**
   * Validate sync operation with UI feedback.
   */
  async validateSync(workspacePath: string): Promise<any> {
    try {
      // Show overlay for validation
      this._showOverlay("Validating sync operation...");
      
      // Dynamic import to avoid circular dependencies
      const { gitLockSignAPI } = await import('./api');
      const result = await gitLockSignAPI.validateSync(workspacePath);
      
      if (result.success) {
        this._updateOverlayMessage("Sync validation completed successfully!");
        await this._delay(1000);
        console.log('✅ Sync validation completed successfully');
        
        // Show validation results
        if (result.warnings.length > 0 || result.critical_issues.length > 0) {
          this._updateOverlayMessage(`Validation completed with ${result.warnings.length} warnings and ${result.critical_issues.length} critical issues`);
          await this._delay(2000);
        }
      } else {
        this._updateOverlayMessage("Sync validation failed");
        await this._delay(1000);
        console.error('❌ Sync validation failed:', result.error);
      }
      
      return result;
      
    } catch (error) {
      this._updateOverlayMessage("Sync validation failed");
      await this._delay(1000);
      console.error('❌ Sync validation error:', error);
      return { 
        success: false, 
        error: `Sync validation failed: ${error}`,
        warnings: [],
        critical_issues: [],
        recommendations: []
      };
    } finally {
      this._hideOverlay();
    }
  }

  /**
   * Check if session initialization is in progress.
   */
  get isInitializing(): boolean {
    return this._isInitializing;
  }

  /**
   * Utility method to add delay for better UX.
   */
  private async _delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

    /**
   * Refresh the file browser using the proper JupyterLab token system.
   * This is much more reliable than DOM-based approaches.
   */
  private async _refreshFileBrowser(): Promise<void> {
    const maxRetries = 3;
    let refreshSuccess = false;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        // Use the proper file browser token - this is the reliable approach
        await this._fileBrowser.model.refresh();
        refreshSuccess = true;
        break;
        
      } catch (error) {
        if (attempt < maxRetries) {
          await this._delay(attempt * 200); // Progressive delay
        }
      }
    }
    
    // If the token-based approach failed, try additional methods as fallback
    if (!refreshSuccess) {
      try {
        // Fallback: try forcing a contents manager refresh
        await this._serviceManager.contents.get('.', { content: true });
        refreshSuccess = true;
      } catch (error) {
        // Contents manager fallback also failed
      }
    }
  }



  /**
   * Check if we should navigate to work subdirectory based on configuration.
   */
  private async _checkWorkSubdirectoryNavigation(baseWorkspacePath: string): Promise<boolean> {
    try {
      console.log('🔍 [SESSION-MANAGER] Checking if work subdirectory navigation is needed...');
      
      // Check if the working directory returned by the API is different from the base workspace
      // This indicates that CREATE_WORK_SUBDIRECTORY is enabled
      const { gitLockSignAPI } = await import('./api');
      const data = await gitLockSignAPI.getWorkingDirectory();
      
      if (data.success && data.working_directory) {
        const workingDir = data.working_directory;
        const isWorkSubdir = workingDir.endsWith('/work') && workingDir.startsWith(baseWorkspacePath);
        
        console.log(`📁 [SESSION-MANAGER] Base workspace: ${baseWorkspacePath}`);
        console.log(`📁 [SESSION-MANAGER] Working directory: ${workingDir}`);
        console.log(`🔍 [SESSION-MANAGER] Work subdirectory navigation needed: ${isWorkSubdir}`);
        
        return isWorkSubdir;
      }
      
      console.log('⚠️ [SESSION-MANAGER] Could not determine working directory, skipping navigation');
      return false;
    } catch (error) {
      console.warn('⚠️ [SESSION-MANAGER] Error checking work subdirectory navigation:', error);
      return false;
    }
  }

  /**
   * Navigate JupyterLab file browser to the work subdirectory.
   */
  private async _navigateToWorkDirectory(baseWorkspacePath: string): Promise<void> {
    try {
      console.log('🚀 [SESSION-MANAGER] Navigating to work subdirectory...');
      
      // Calculate the work subdirectory path relative to JupyterLab's root
      const workRelativePath = 'work';
      
      console.log(`📁 [SESSION-MANAGER] Navigating file browser to: ${workRelativePath}`);
      
      // Use the file browser model to navigate to the work directory
      await this._fileBrowser.model.cd(workRelativePath);
      
      console.log('✅ [SESSION-MANAGER] Successfully navigated to work directory');
      
      // Also refresh the file browser to ensure it shows the contents
      await this._fileBrowser.model.refresh();
      
      console.log('✅ [SESSION-MANAGER] File browser refreshed in work directory');
      
    } catch (error) {
      console.error('❌ [SESSION-MANAGER] Failed to navigate to work directory:', error);
      
      // If navigation fails, try an alternative approach
      try {
        console.log('🔄 [SESSION-MANAGER] Attempting alternative navigation method...');
        
        // Try using the contents manager directly
        const contents = await this._serviceManager.contents.get('work', { content: true });
        if (contents.type === 'directory') {
          await this._fileBrowser.model.cd('work');
          console.log('✅ [SESSION-MANAGER] Alternative navigation successful');
        }
      } catch (altError) {
        console.error('❌ [SESSION-MANAGER] Alternative navigation also failed:', altError);
      }
    }
  }

  /**
   * Dispose of the session manager.
   */
  dispose(): void {
    this._hideOverlay();
    this._isInitializing = false;
  }
} 