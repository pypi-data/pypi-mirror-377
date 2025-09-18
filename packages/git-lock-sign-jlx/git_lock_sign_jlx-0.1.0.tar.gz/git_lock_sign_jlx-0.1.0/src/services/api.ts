/**
 * API service for communicating with the CELN sidecar service.
 */

import {
  ILockNotebookRequest,
  ILockNotebookResponse,
  IUnlockNotebookRequest,
  IUnlockNotebookResponse,
  IUserInfoResponse,
  INotebookStatusResponse,
  ICommitNotebookRequest,
  ICommitNotebookResponse,
  IProvisionRepositoryResponse,
  IPushRepositoryResponse,
  IAutoPushResponse,
  IAutoCommitResponse,
  IButtonConfiguration,
  IConfigResponse,
  ISidecarUrlResponse
} from '../types';

import { ServerConnection } from '@jupyterlab/services';
import { URLExt } from '@jupyterlab/coreutils';



/**
 * Cache for the server root directory to avoid repeated API calls
 */
let _serverRootCache: string | null = null;

/**
 * Get the server root directory by querying our backend extension
 */
async function getServerRoot(): Promise<string> {
  if (_serverRootCache) {
    return _serverRootCache as string;
  }

  try {

    // Try to get the working directory from our own backend extension
    try {
      const data = await gitLockSignAPI.getWorkingDirectory();
      if (data.working_directory) {
        _serverRootCache = data.working_directory;
        return _serverRootCache as string;
      }
    } catch (error) {
      // Backend API failed, will use fallback
    }

    // If our backend endpoint isn't available, we cannot proceed
    throw new Error('Could not determine server working directory. Backend extension may not be properly installed.');

  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error('[getServerRoot] Failed to determine server root:', errorMessage);
    throw new Error(`Cannot determine server working directory: ${errorMessage}. Please ensure the backend extension is properly configured.`);
  }
}

/**
 * Utility function to get the absolute path for a notebook given its JupyterLab-relative path.
 */
export async function getAbsoluteNotebookPath(relativePath: string): Promise<string> {
  const serverRoot = await getServerRoot();

  // Clean up the relative path and strip RTC prefix
  let cleanRelPath = stripRTCPrefix(relativePath).replace(/^\/+/, '');

  // Fix for CREATE_WORK_SUBDIRECTORY: if server root ends with '/work' and 
  // relative path starts with 'work/', strip the duplicate 'work/' prefix
  if (serverRoot.endsWith('/work') && cleanRelPath.startsWith('work/')) {
    cleanRelPath = cleanRelPath.substring(5); // Remove 'work/' prefix
  }

  // Construct the absolute path
  const absolutePath = cleanRelPath ? `${serverRoot}/${cleanRelPath}` : serverRoot;
  return absolutePath;
}

/**
 * Check if RTC (Real-Time Collaboration) handling is enabled
 * This can be disabled via URL parameter when RTC is disabled at server level
 */
export function isRTCHandlingEnabled(): boolean {
  // Check for URL parameter or global window variable that disables RTC handling
  // This can be set when RTC is disabled at the server level
  try {
    // Check URL parameters first
    const urlParams = new URLSearchParams(window.location.search);
    const rtcParam = urlParams.get('enable_rtc_handling');
    if (rtcParam !== null) {
      return !['false', '0', 'off', 'disabled'].includes(rtcParam.toLowerCase());
    }
    
    // Check for global configuration (can be set by server-side template)
    const globalConfig = (window as any).JUPYTER_CONFIG_DATA;
    if (globalConfig && globalConfig.enable_rtc_handling !== undefined) {
      const rtcHandlingEnabled = globalConfig.enable_rtc_handling;
      if (typeof rtcHandlingEnabled === 'boolean') {
        return rtcHandlingEnabled;
      }
      if (typeof rtcHandlingEnabled === 'string') {
        return !['false', '0', 'off', 'disabled'].includes(rtcHandlingEnabled.toLowerCase());
      }
    }
  } catch (error) {
    console.warn('Error checking RTC handling configuration:', error);
  }
  
  // Default to false when RTC is disabled at server level
  // Since we've disabled RTC in the Docker configuration, default to false
  return false;
}

/**
 * Strip RTC (Real-Time Collaboration) prefix from JupyterLab paths
 * When RTC is disabled at server level, always strip to match disk files
 * When RTC is enabled at server level, only strip if we want frontend handling
 */
export function stripRTCPrefix(path: string): string {
  const rtcHandlingEnabled = isRTCHandlingEnabled();
  
  // INVERTED LOGIC: When RTC is DISABLED, we ALWAYS strip to match disk files
  // When RTC is ENABLED, we only strip if RTC handling is enabled
  if (!rtcHandlingEnabled) {
    // RTC disabled at server level - always strip to match disk files
    if (path.startsWith('RTC:')) {
      return path.substring(4); // Remove "RTC:" prefix
    }
    return path;
  }
  
  // RTC enabled at server level - only strip if RTC handling is enabled
  if (path.startsWith('RTC:')) {
    return path.substring(4); // Remove "RTC:" prefix
  }
  return path;
}

/**
 * Synchronous version that uses cached server root (call getAbsoluteNotebookPath first to populate cache)
 */
export function getAbsoluteNotebookPathSync(relativePath: string): string {
  if (!_serverRootCache) {
    throw new Error('Server root not initialized. Call getAbsoluteNotebookPath() first to initialize the cache.');
  }

  // Clean up the relative path and strip RTC prefix
  let cleanRelPath = stripRTCPrefix(relativePath).replace(/^\/+/, '');

  // Fix for CREATE_WORK_SUBDIRECTORY: if server root ends with '/work' and 
  // relative path starts with 'work/', strip the duplicate 'work/' prefix
  if (_serverRootCache.endsWith('/work') && cleanRelPath.startsWith('work/')) {
    cleanRelPath = cleanRelPath.substring(5); // Remove 'work/' prefix
  }

  // Construct the absolute path
  const absolutePath = cleanRelPath ? `${_serverRootCache}/${cleanRelPath}` : _serverRootCache;
  return absolutePath;
}

/**
 * API service class for CELN sidecar operations.
 */
export class GitLockSignAPI {
  private _sidecarUrl: string;
  private _isHealthy: boolean = false;
  private _lastHealthCheck: number = 0;
  private _healthCheckInterval: number = 30000; // Default 30 seconds, will be updated from config
  private _healthCheckTimeout: number = 5000; // Default 5 seconds, will be updated from config
  private _apiRequestTimeout: number = 180000; // Default 3 minutes for git operations, will be updated from config
  private _useBackendHandlers: boolean = true; // NEW: Use backend handlers instead of direct sidecar
  private _buttonConfig: IButtonConfiguration | null = null; // Cache button configuration
  private _configLoaded: boolean = false; // Track if config has been loaded

  constructor() {
    // Sidecar URL will be retrieved from dedicated sidecar URL handler
    this._sidecarUrl = '';
    this._initializeSidecarUrl();
  }

  /**
   * Get sidecar URL from dedicated JupyterLab backend handler.
   */
  private async _getSidecarUrl(): Promise<ISidecarUrlResponse> {
    try {
      return await this._makeBackendRequest<ISidecarUrlResponse>('/sidecar-url', {}, 'GET');
    } catch (error) {
      console.error('Error getting sidecar URL:', error);
      return {
        success: false,
        message: `Failed to get sidecar URL: ${error}`
      };
    }
  }

  /**
   * Initialize sidecar URL by fetching from dedicated JupyterLab backend handler.
   */
  private async _initializeSidecarUrl(): Promise<void> {
    try {
      console.log('[SIDECAR-URL] Getting sidecar URL from JupyterLab backend...');
      
      // Call dedicated sidecar URL handler
      const sidecarUrlResponse = await this._getSidecarUrl();
      
      if (sidecarUrlResponse.success && sidecarUrlResponse.sidecar_host && sidecarUrlResponse.sidecar_port) {
        
        // Build sidecar URL from environment variables
        // For Kubernetes compatibility, always use the same protocol as the current page
        // This prevents mixed content issues when JupyterLab is served over HTTPS
        const protocol = `http://`;
        this._sidecarUrl = `${protocol}${sidecarUrlResponse.sidecar_host}:${sidecarUrlResponse.sidecar_port}`;
        
        console.log(`✅ Sidecar URL configured: ${this._sidecarUrl}`);
        
        // Now initialize configuration using the correct sidecar URL
        this._initializeConfigSync();
      } else {
        console.error('❌ Failed to get sidecar URL from backend');
        throw new Error('Failed to get sidecar URL');
      }
    } catch (error) {
      console.error('❌ Failed to initialize sidecar URL:', error);
      // Use fallback with same protocol as current page for Kubernetes compatibility
      const fallbackProtocol = `http://`;
      this._sidecarUrl = `${fallbackProtocol}0.0.0.0:8001`
      console.warn(`⚠️ Using fallback sidecar URL: ${this._sidecarUrl}`);
      
      // Still try to initialize config with fallback URL
      this._initializeConfigSync();
    }
  }

  /**
   * Initialize configuration by fetching from sidecar service.
   * Sidecar URL must already be set before calling this method.
   */
  private _initializeConfigSync(): void {
    // Fetch config from sidecar (URL already set by sidecar URL handler)
    this.getConfig().then(config => {
      if (config.success) {
        console.log('✅ Configuration loaded from sidecar');
        
        // Update timeout configurations
        if (config.health_check_interval_ms) {
          this._healthCheckInterval = config.health_check_interval_ms;
        }
        if (config.health_check_timeout_ms) {
          this._healthCheckTimeout = config.health_check_timeout_ms;
        }
        if (config.api_request_timeout_ms) {
          this._apiRequestTimeout = config.api_request_timeout_ms;
        }
        
        this._configLoaded = true;
      } else {
        console.warn('⚠️ Failed to get configuration from sidecar (using defaults)');
        this._configLoaded = true;
      }
      
      // Start health checks after config initialization
      this._checkSidecarHealth();
    }).catch(error => {
      console.error('❌ Failed to initialize config from sidecar:', error);
      this._configLoaded = true;
      // Start health checks even if config failed
      this._checkSidecarHealth();
    });
  }

  /**
   * Check if sidecar service is healthy.
   */
  private async _checkSidecarHealth(): Promise<boolean> {
    const now = Date.now();

    // Only check health every 30 seconds
    if (now - this._lastHealthCheck < this._healthCheckInterval && this._isHealthy) {
      return this._isHealthy;
    }
    
    if (this._useBackendHandlers) {
      // Use backend health endpoint (Kubernetes-compatible)
      try {
        const response = await this._makeRequest<{healthy: boolean, message?: string, error?: string}>('/health', {}, 'GET');
        
        this._isHealthy = response.healthy;
        this._lastHealthCheck = now;

        if (!this._isHealthy) {
          console.error(`❌ Sidecar health check failed: ${response.error}`);
          this._showSidecarError('Sidecar service is not responding properly');
        }

      } catch (error) {
        this._isHealthy = false;
        this._lastHealthCheck = now;
        console.error('❌ Sidecar health check error:', error);
        this._showSidecarError('Cannot connect to sidecar service');
      }
    } else {
      // Use direct sidecar health check (legacy mode)
      try {
        const healthUrl = `${this._sidecarUrl}/health`;
        
        const response = await fetch(healthUrl, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
          signal: AbortSignal.timeout(this._healthCheckTimeout)
        });

        this._isHealthy = response.ok;
        this._lastHealthCheck = now;

        if (!this._isHealthy) {
          console.error('❌ Sidecar health check failed:', response.status, response.statusText);
          this._showSidecarError('Sidecar service is not responding properly');
        }

      } catch (error) {
        this._isHealthy = false;
        this._lastHealthCheck = now;
        console.error('❌ Sidecar health check error:', error);
        this._showSidecarError('Cannot connect to sidecar service');
      }
    }

    return this._isHealthy;
  }

  /**
   * Show error when sidecar is unavailable.
   */
  private _showSidecarError(message: string): void {
    // Create a prominent error notification
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 10px;
      right: 10px;
      background: #f44336;
      color: white;
      padding: 15px;
      border-radius: 5px;
      z-index: 10000;
      max-width: 400px;
      font-family: Arial, sans-serif;
      box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    `;
    notification.innerHTML = `
      <strong>CELN Service Error</strong><br>
      ${message}<br>
      <small>Notebook operations are disabled until the service is restored.</small>
    `;

    document.body.appendChild(notification);

    // Remove after 10 seconds
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 10000);
  }

  /**
   * Ensure sidecar is healthy before making requests.
   */
  private async _ensureSidecarHealth(): Promise<void> {
    const isHealthy = await this._checkSidecarHealth();
    if (!isHealthy) {
      throw new Error('Sidecar service is not available. Cannot proceed with notebook operations.');
    }
  }

  /**
   * Get the XSRF token from cookies or meta tags.
   */
  private _getXsrfToken(): string {
    // Try to get XSRF token from cookie first
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === '_xsrf') {
        return decodeURIComponent(value);
      }
    }
    
    // Fallback: try to get from meta tag
    const metaTag = document.querySelector('meta[name="_xsrf"]') as HTMLMetaElement;
    if (metaTag) {
      return metaTag.content;
    }
    
    // If all else fails, return empty string (this will likely cause the request to fail)
    return '';
  }

  /**
   * Make a request to either backend handlers or sidecar service.
   */
  private async _makeRequest<T>(
    endpoint: string,
    options: RequestInit = {},
    method: string = 'POST'
  ): Promise<T> {
    if (this._useBackendHandlers) {
      // Use backend handlers (will show sidecar_client.py logs)
      return this._makeBackendRequest<T>(endpoint, options, method);
    } else {
      // Use direct sidecar calls (original behavior)
      return this._makeSidecarRequest<T>(endpoint, options, method);
    }
  }

  /**
   * Make a request to backend handlers.
   */
  private async _makeBackendRequest<T>(
    endpoint: string,
    options: RequestInit = {},
    method: string = 'POST'
  ): Promise<T> {
    const serverSettings = ServerConnection.makeSettings();
    const baseUrl = serverSettings.baseUrl;
    const url = URLExt.join(baseUrl, `/git-lock-sign${endpoint}`);

    // Validate URL construction
    if (!baseUrl) {
      console.error(`❌ Backend request failed: baseUrl is empty or null!`);
    }
    if (baseUrl && !baseUrl.startsWith('http')) {
      console.warn(`⚠️ Backend request warning: baseUrl doesn't start with http/https: "${baseUrl}"`);
    }

    const defaultOptions: RequestInit = {
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `token ${serverSettings.token}`,
        'X-XSRFToken': this._getXsrfToken(),
        ...options.headers
      },
      signal: AbortSignal.timeout(this._apiRequestTimeout)
    };

    const finalOptions = { ...defaultOptions, ...options };

    try {
      const response = await fetch(url, finalOptions);


      if (!response.ok) {
        // Try to extract error details from response body for 500 errors
        let errorMessage = `Backend request failed: ${response.status} ${response.statusText}`;
        
        if (response.status === 500) {
          try {
            const errorData = await response.json();
            if (errorData && errorData.error) {
              errorMessage = errorData.error;
            }
          } catch (parseError) {
            // Could not parse error response, use default message
          }
        }
        
        throw new Error(errorMessage);
      }

      return await response.json();
    } catch (error) {
      console.error(`❌ Backend request to ${endpoint} failed:`, error);
      throw error;
    }
  }

  /**
   * Make a request to the sidecar service directly.
   */
  private async _makeSidecarRequest<T>(
    endpoint: string,
    options: RequestInit = {},
    method: string = 'POST'
  ): Promise<T> {
    await this._ensureSidecarHealth();

    const url = `${this._sidecarUrl}/sidecar${endpoint}`;

    const defaultOptions: RequestInit = {
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'X-XSRFToken': this._getXsrfToken(),
        ...options.headers
      },
      signal: AbortSignal.timeout(this._apiRequestTimeout)
    };

    const finalOptions = { ...defaultOptions, ...options };

    try {
      const response = await fetch(url, finalOptions);

      if (!response.ok) {
        // Try to extract error details from response body for 500 errors
        let errorMessage = `Sidecar request failed: ${response.status} ${response.statusText}`;
        
        if (response.status === 500) {
          try {
            const errorData = await response.json();
            if (errorData && errorData.error) {
              errorMessage = errorData.error;
            }
          } catch (parseError) {
            // Could not parse error response, use default message
          }
        }
        
        throw new Error(errorMessage);
      }

      return await response.json();
    } catch (error) {
      console.error(`Sidecar request to ${endpoint} failed:`, error);
      throw error;
    }
  }

  /**
   * Lock and sign a notebook.
   */
  async lockNotebook(
    notebookPath: string,
    notebookContent: any,
    commitMessage?: string
  ): Promise<ILockNotebookResponse> {
    const request: ILockNotebookRequest = {
      notebook_path: notebookPath,
      notebook_content: notebookContent,
      commit_message: commitMessage
    };

    try {
      const response = await this._makeRequest<ILockNotebookResponse>('/lock', {
        method: 'POST',
        body: JSON.stringify(request)
      });

      return response;
    } catch (error) {
      console.error('Error locking notebook:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : `Failed to lock notebook: ${error}`
      };
    }
  }

  /**
   * Unlock a notebook after signature verification.
   */
  async unlockNotebook(
    notebookPath: string,
    notebookContent: any
  ): Promise<IUnlockNotebookResponse> {
    const request: IUnlockNotebookRequest = {
      notebook_path: notebookPath,
      notebook_content: notebookContent
    };

    try {
      const response = await this._makeRequest<IUnlockNotebookResponse>('/unlock', {
        method: 'POST',
        body: JSON.stringify(request)
      });

      return response;
    } catch (error) {
      console.error('Error unlocking notebook:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : `Failed to unlock notebook: ${error}`
      };
    }
  }

  /**
   * Get git user information for a specific notebook path.
   */
  async getUserInfo(notebookPath: string): Promise<IUserInfoResponse> {
    try {
      const response = await this._makeRequest<IUserInfoResponse>(`/user-info?notebook_path=${encodeURIComponent(notebookPath)}`, {
        method: 'GET'
      });
      return response;
    } catch (error) {
      console.error('Error getting user info:', error);
      return {
        success: false,
        error: `Failed to get user info: ${error}`
      };
    }
  }

  /**
   * Initialize git repository for a notebook directory.
   */
  async initGitRepository(notebookPath: string): Promise<any> {
    const request = {
      notebook_path: notebookPath
    };

    try {
      const response = await this._makeRequest('/git-init', {
        method: 'POST',
        body: JSON.stringify(request)
      });

      return response;
    } catch (error) {
      console.error('Error initializing git repository:', error);
      return {
        success: false,
        error: `Failed to initialize git repository: ${error}`
      };
    }
  }

  /**
   * Auto-commit notebook changes.
   */
  async autoCommit(
    notebookPath: string,
    cellContentPreview?: string,
    executionCount?: number
  ): Promise<IAutoCommitResponse> {
    const request = {
      notebook_path: notebookPath,
      auto_commit: true,
      cell_content_preview: cellContentPreview,
      execution_count: executionCount,
      timestamp: new Date().toISOString()
    };

    console.log('🚀 Starting auto-commit for:', notebookPath);

    try {
      const response = await this._makeRequest<IAutoCommitResponse>('/commit', {
        method: 'POST',
        body: JSON.stringify(request)
      });

      if (response.success) {
        if (response.debounced) {
          console.log('⏱️ Auto-commit debounced - scheduled for later');
        } else {
          console.log('✅ Auto-commit completed successfully');
        }
      } else {
        console.error('❌ Auto-commit failed:', response.error);
      }

      return response;
    } catch (error) {
      console.error('❌ Auto-commit error:', error);
      return {
        success: false,
        error: `Failed to auto-commit notebook: ${error}`
      };
    }
  }

  /**
   * Auto-commit notebook changes with explicit content.
   * This ensures the latest notebook content is committed even if not yet saved to disk.
   */
  async autoCommitWithContent(
    notebookPath: string,
    notebookContent: any,
    cellContentPreview?: string,
    executionCount?: number
  ): Promise<IAutoCommitResponse> {
    const request = {
      notebook_path: notebookPath,
      notebook_content: notebookContent,
      auto_commit: true,
      cell_content_preview: cellContentPreview,
      execution_count: executionCount,
      timestamp: new Date().toISOString()
    };

    console.log('🚀 Starting auto-commit with content for:', notebookPath);

    try {
      const response = await this._makeRequest<IAutoCommitResponse>('/commit', {
        method: 'POST',
        body: JSON.stringify(request)
      });

      if (response.success) {
        if (response.debounced) {
          console.log('⏱️ Auto-commit with content debounced - scheduled for later');
        } else {
          console.log('✅ Auto-commit with content completed successfully');
        }
      } else {
        console.error('❌ Auto-commit with content failed:', response.error);
      }

      return response;
    } catch (error) {
      console.error('❌ Auto-commit with content error:', error);
      return {
        success: false,
        error: `Failed to auto-commit notebook with content: ${error}`
      };
    }
  }

  /**
   * Auto-push notebook changes.
   */
  async autoPush(notebookPath: string): Promise<IAutoPushResponse> {
    const request = {
      notebook_path: notebookPath,
      auto_push: true,
      auto_commit_before_push: true  // Capture any uncommitted changes before pushing
    };

    console.log('🚀 Starting auto-push for:', notebookPath);

    try {
      const response = await this._makeRequest<IAutoPushResponse>('/push', {
        method: 'POST',
        body: JSON.stringify(request)
      });

      // Log the response details
      if (response.success) {
        if (response.debounced) {
          console.log('⏱️ Auto-push debounced - scheduled for later');
        } else {
          console.log('✅ Auto-push completed successfully');
        }
      } else {
        console.error('❌ Auto-push failed:', response.error);
      }

      return response;
    } catch (error) {
      console.error('❌ Auto-push error:', error);
      return {
        success: false,
        error: `Failed to auto-push notebook: ${error}`
      };
    }
  }

  /**
   * Check notebook lock status and signature validity.
   */
  async checkNotebookStatus(
    notebookContent: any,
    notebookPath?: string
  ): Promise<INotebookStatusResponse> {
    try {
      const response = await this._makeRequest<INotebookStatusResponse>(`/status?notebook_path=${encodeURIComponent(notebookPath || '')}`, {
        method: 'GET'
      });

      return response;
    } catch (error) {
      console.error('Error checking notebook status:', error);
      return {
        success: false,
        error: `Failed to check notebook status: ${error}`
      };
    }
  }

  /**
   * Commit notebook changes to git.
   */
  async commitNotebook(
    request: ICommitNotebookRequest
  ): Promise<ICommitNotebookResponse> {
    const sidecarRequest = {
      notebook_path: request.notebook_path,
      commit_message: request.commit_message,
      auto_commit: false
    };

    try {
      const response = await this._makeRequest<ICommitNotebookResponse>('/commit', {
        method: 'POST',
        body: JSON.stringify(sidecarRequest)
      });

      return response;
    } catch (error) {
      console.error('Error committing notebook:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : `Failed to commit notebook: ${error}`
      };
    }
  }

  /**
   * Get git repository status for a notebook.
   */
  async getRepositoryStatus(notebookPath: string): Promise<any> {
    try {
      const response = await this._makeRequest(`/status?notebook_path=${encodeURIComponent(notebookPath)}`, {
        method: 'GET'
      });

      return response;
    } catch (error) {
      console.error('Error getting repository status:', error);
      return {
        success: false,
        error: `Failed to get repository status: ${error}`
      };
    }
  }

  /**
   * Push changes to the remote repository.
   */
  async pushToRepository(
    notebookPath: string,
    pushUrl?: string
  ): Promise<IPushRepositoryResponse> {
    const request = {
      notebook_path: notebookPath,
      auto_push: false,
      auto_commit_before_push: true  // Enable auto-commit for manual pushes too
    };

    console.log('🚀 Starting manual push for:', notebookPath);

    try {
      const response = await this._makeRequest<IPushRepositoryResponse>('/push', {
        method: 'POST',
        body: JSON.stringify(request)
      });

      if (response.success) {
        console.log('✅ Manual push completed successfully');
      } else {
        console.error('❌ Manual push failed:', response.error);
      }

      return response;
    } catch (error) {
      console.error('❌ Manual push error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : `Failed to push to repository: ${error}`
      };
    }
  }

  /**
   * Provision GitLab repository integration.
   */
  async provisionRepository(notebookPath: string): Promise<IProvisionRepositoryResponse> {
    try {
      // notebookPath is already absolute when passed from NotebookLockManager
      const response = await this._makeRequest('/provision', {
        body: JSON.stringify({ notebook_path: notebookPath })
      });

      return {
        success: (response as any).success,
        message: (response as any).message,
        repo_url: (response as any).repository_url,
        push_url: (response as any).repository_url,
        error: (response as any).error
      };
    } catch (error) {
      console.error('Error provisioning repository:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : `Failed to provision repository: ${error}`
      };
    }
  }

  /**
   * Initialize session with workspace-level repository setup and sync.
   * Called when JupyterLab starts up to ensure user's workspace is ready.
   */
  async initializeSession(workspacePath: string): Promise<IProvisionRepositoryResponse> {
    try {
      console.log('🚀 Initializing session for workspace:', workspacePath);
      
      const response = await this._makeRequest('/session-init', {
        body: JSON.stringify({ workspace_path: workspacePath })
      });

      const result = {
        success: (response as any).success,
        message: (response as any).message,
        repo_url: (response as any).repository_url,
        push_url: (response as any).repository_url,
        error: (response as any).error
      };

      if (result.success) {
        console.log('✅ Session initialization completed successfully');
      } else {
        console.error('❌ Session initialization failed:', result.error);
      }

      return result;
    } catch (error) {
      console.error('❌ Session initialization error:', error);
      return {
        success: false,
        error: `Failed to initialize session: ${error}`
      };
    }
  }

  /**
   * Validate sync operation to identify potential issues before proceeding.
   * This allows users to check repository state before syncing.
   */
  async validateSync(workspacePath: string): Promise<any> {
    try {
      console.log('🚀 Validating sync for workspace:', workspacePath);
      
      const response = await this._makeRequest('/validate-sync', {
        body: JSON.stringify({ workspace_path: workspacePath })
      });

      const result = {
        success: (response as any).valid,
        valid: (response as any).valid,
        warnings: (response as any).warnings || [],
        critical_issues: (response as any).critical_issues || [],
        recommendations: (response as any).recommendations || [],
        user_config_mismatch: (response as any).user_config_mismatch || false,
        uncommitted_changes: (response as any).uncommitted_changes || false,
        untracked_files: (response as any).untracked_files || false,
        sync_required: (response as any).sync_required || false,
        error: (response as any).error
      };

      if (result.success) {
        console.log('✅ Sync validation completed successfully');
        if (result.warnings.length > 0) {
          console.warn(`⚠️ Validation warnings: ${result.warnings.length}`);
        }
        if (result.critical_issues.length > 0) {
          console.error(`❌ Validation critical issues: ${result.critical_issues.length}`);
        }
      } else {
        console.error('❌ Sync validation failed:', result.error);
      }

      return result;
    } catch (error) {
      console.error('❌ Sync validation error:', error);
      return {
        success: false,
        valid: false,
        warnings: [],
        critical_issues: [],
        recommendations: [],
        user_config_mismatch: false,
        uncommitted_changes: false,
        untracked_files: false,
        sync_required: false,
        error: `Failed to validate sync: ${error}`
      };
    }
  }



  /**
   * Manually sync local repository with remote history.
   */
  async syncWithRemote(notebookPath: string): Promise<any> {
    try {
      console.log('🚀 Starting manual sync with remote for:', notebookPath);
      
      const response = await this._makeRequest('/sync', {
        body: JSON.stringify({ notebook_path: notebookPath })
      });

      const result = {
        success: (response as any).success,
        is_git_repository: (response as any).is_git_repository,
        is_locked: (response as any).is_locked,
        repository_path: (response as any).repository_path,
        last_commit_hash: (response as any).last_commit_hash,
        error: (response as any).error
      };

      if (result.success) {
        console.log('✅ Remote sync completed successfully');
      } else {
        console.error('❌ Remote sync failed:', result.error);
      }

      return result;
    } catch (error) {
      console.error('❌ Remote sync error:', error);
      return {
        success: false,
        is_git_repository: false,
        is_locked: false,
        repository_path: '',
        last_commit_hash: '',
        error: `Failed to sync with remote: ${error}`
      };
    }
  }

  /**
   * Fetch configuration from sidecar.
   */
  async getConfig(): Promise<IConfigResponse> {
    try {
      const response = await this._makeRequest<IConfigResponse>('/config', {}, 'GET');

      // Cache button configuration
      if (response.success) {
        this._buttonConfig = {
          enable_commit_button: response.enable_commit_button ?? true,
          enable_push_button: response.enable_push_button ?? true,
          enable_lock_button: response.enable_lock_button ?? true
        };
      }

      return response;
    } catch (error) {
      console.error('Error fetching config:', error);
      return {
        success: false,
        error: `Failed to fetch config: ${error}`,
        cell_execution_detection_delay_ms: 1000, // Default fallback
        enable_commit_button: true,
        enable_push_button: true,
        enable_lock_button: true
      };
    }
  }

  /**
   * Get cached button configuration.
   */
  getButtonConfig(): IButtonConfiguration {
    return this._buttonConfig || {
      enable_commit_button: true,
      enable_push_button: true,
      enable_lock_button: true
    };
  }

  /**
   * Get working directory from backend handler.
   */
  async getWorkingDirectory(): Promise<any> {
    return await this._makeRequest('/working-directory', {}, 'GET');
  }

  /**
   * Commit file lifecycle changes (creation/deletion).
   */
  async commitFileLifecycle(requestBody: any): Promise<any> {
    return await this._makeRequest('/file-lifecycle-commit', {
      method: 'POST',
      body: JSON.stringify(requestBody)
    });
  }

  /**
   * Get notification auto-dismiss timeout from config (fallback to 5000ms).
   */
  async getNotificationTimeout(): Promise<number> {
    try {
      if (!this._configLoaded) {
        const config = await this.getConfig();
        return config.notification_auto_dismiss_ms ?? 5000;
      }
      // If config is already loaded, we need to fetch it fresh since we don't cache this value
      const config = await this.getConfig();
      return config.notification_auto_dismiss_ms ?? 5000;
    } catch (error) {
      console.error('Failed to get notification timeout from config:', error);
      return 5000; // Default fallback
    }
  }
}

/**
 * Singleton instance of the API service.
 */
export const gitLockSignAPI = new GitLockSignAPI();


