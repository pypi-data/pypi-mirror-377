/**
 * Type definitions for git-based notebook locking and signing.
 */

export interface ISignatureMetadata {
  locked: boolean;
  signature: string;
  user_name: string;
  user_email: string;
  timestamp: string;
  content_hash: string;
  unlocked_by_user_name?: string;
  unlock_timestamp?: string;
}

export interface IUserInfo {
  name: string;
  email: string;
  gpgKeyId?: string;
}

export interface INotebookStatus {
  locked: boolean;
  signature_valid: boolean;
  message: string;
  metadata?: ISignatureMetadata;
}

export interface IApiResponse<T = any> {
  success: boolean;
  message?: string;
  error?: string;
  data?: T;
}

export interface ILockNotebookRequest {
  notebook_path: string;
  notebook_content: any;
  commit_message?: string;
}

export interface ILockNotebookResponse extends IApiResponse {
  metadata?: ISignatureMetadata;
  commit_hash?: string;
  signed?: boolean;
}

export interface IUnlockNotebookRequest {
  notebook_path: string;
  notebook_content: any;
}

export interface IUnlockNotebookResponse extends IApiResponse {
  metadata?: ISignatureMetadata;
  commit_hash?: string;
  signature_verification_passed?: boolean;
  was_gpg_signed?: boolean;
}

export interface IUserInfoResponse {
  success: boolean;
  user_name?: string;
  user_email?: string;
  gpg_key_id?: string;
  error?: string;
}

export interface INotebookStatusRequest {
  notebook_content: any;
  notebook_path?: string;
}

export interface INotebookStatusResponse extends IApiResponse {
  locked?: boolean;
  signature_valid?: boolean;
  metadata?: ISignatureMetadata;
}

export interface ILockButtonState {
  locked: boolean;
  loading: boolean;
  error: string | null;
  signatureInfo: ISignatureMetadata | null;
}

export enum LockButtonAction {
  LOCK = 'lock',
  UNLOCK = 'unlock'
}

export interface ICommitNotebookRequest {
  notebook_path: string;
  notebook_content: any;
  commit_message: string;
}

export interface ICommitNotebookResponse extends IApiResponse {
  commit_hash?: string;
  signed?: boolean;
}

export interface IProvisionRepositoryRequest {
  notebook_path: string;
}

export interface IProvisionRepositoryResponse extends IApiResponse {
  push_url?: string;
  repo_url?: string;
}

export interface IPushRepositoryRequest {
  notebook_path: string;
  push_url: string;
}

export interface IPushRepositoryResponse extends IApiResponse {
  message?: string;
}

export interface IPushButtonState {
  loading: boolean;
  error: string | null;
  lastPushTime?: string;
}

export interface INotebookLockManager {
  isLocked: boolean;
  signatureMetadata: ISignatureMetadata | null;
  lockNotebook(): Promise<boolean>;
  unlockNotebook(): Promise<boolean>;
  commitNotebook(): Promise<boolean>;
  pushNotebook(): Promise<boolean>;
  checkStatus(): Promise<INotebookStatus>;
  getUserInfo(): Promise<IUserInfo | null>;
}

export interface IAutoPushResponse extends IApiResponse {
  repository_url?: string;
  debounced?: boolean;
}

export interface IAutoCommitResponse extends IApiResponse {
  commit_hash?: string;
  signed?: boolean;
  debounced?: boolean;
  metadata?: ISignatureMetadata;
  content_hash?: string;
}

export interface IButtonConfiguration {
  enable_commit_button: boolean;
  enable_push_button: boolean;
  enable_lock_button: boolean;
}

export interface IPushButtonState {
  loading: boolean;
  error: string | null;
  lastPushTime?: string;
  shouldRender: boolean;
}

export interface ILockButtonState {
  locked: boolean;
  loading: boolean;
  error: string | null;
  signatureInfo: ISignatureMetadata | null;
  shouldRender: boolean;
}

export interface ISidecarUrlResponse extends IApiResponse {
  sidecar_host?: string;
  sidecar_port?: number;
}

export interface IConfigResponse extends IApiResponse {
  include_metadata?: boolean;
  commit_debounce_seconds?: number;
  push_debounce_seconds?: number;
  cell_execution_detection_delay_ms?: number;
  auto_save_interval_minutes?: number;
  enable_commit_button?: boolean;
  enable_push_button?: boolean;
  enable_lock_button?: boolean;
  enable_file_creation_tracking?: boolean;
  auto_save_enabled?: boolean;
  debug_mode?: boolean;
  health_check_interval_ms?: number;
  health_check_timeout_ms?: number;
  api_request_timeout_ms?: number;
  notification_auto_dismiss_ms?: number;
}
