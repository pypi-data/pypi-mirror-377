/**
 * User info display component for showing git user configuration.
 */

import React, { useState, useEffect } from 'react';

import { ReactWidget } from '@jupyterlab/apputils';
import { NotebookPanel } from '@jupyterlab/notebook';

import { gitLockSignAPI, getAbsoluteNotebookPath } from '../services/api';
import { IUserInfo } from '../types';

/**
 * Props for the UserInfoDisplay component.
 */
interface IUserInfoDisplayProps {
  notebookPanel: any;
}

/**
 * State for the user info display.
 */
interface IUserInfoState {
  userInfo: IUserInfo | null;
  loading: boolean;
  error: string | null;
}

/**
 * React component for displaying git user information.
 */
const UserInfoDisplayComponent: React.FC<IUserInfoDisplayProps> = ({
  notebookPanel
}) => {
  const [state, setState] = useState<IUserInfoState>({
    userInfo: null,
    loading: true,
    error: null
  });

  // Load user info when component mounts
  useEffect(() => {
    const fetchUserInfo = async () => {
      setState(prev => ({ ...prev, loading: true, error: null }));
      try {
        const relativePath = notebookPanel?.context?.path || '';
        const notebookPath = await getAbsoluteNotebookPath(relativePath);
        const response = await gitLockSignAPI.getUserInfo(notebookPath);
        if (response.success) {
          setState({
            userInfo: {
              name: response.user_name || '',
              email: response.user_email || '',
              gpgKeyId: response.gpg_key_id || ''
            },
            loading: false,
            error: null
          });
        } else {
          setState({
            userInfo: null,
            loading: false,
            error: response.error || 'Failed to fetch user info'
          });
        }
      } catch (err) {
        setState({
          userInfo: null,
          loading: false,
          error: 'Failed to fetch user info'
        });
      } finally {
        setState(prev => ({ ...prev, loading: false }));
      }
    };
    fetchUserInfo();
  }, [notebookPanel]);


  /**
   * Render the user info content.
   */
  const renderContent = (): JSX.Element => {
    if (state.loading) {
      return (
        <div className="git-user-info-content loading">
          <span className="jp-Icon jp-CircularProgressIcon" />
          <span className="git-user-text">Loading git user...</span>
        </div>
      );
    }

    if (state.error || !state.userInfo) {
      return (
        <div className="git-user-info-content error">
          <span className="jp-Icon jp-ErrorIcon" />
          <span className="git-user-text">
            Git user not configured
          </span>
        </div>
      );
    }

    return (
      <div className="git-user-info-content success">
        <span className="jp-Icon jp-UserIcon" />
        <span className="git-user-text">
          <strong>{state.userInfo.name}</strong>
        </span>
      </div>
    );
  };

  return (
    <div className="git-user-info-display">
      {renderContent()}
    </div>
  );
};

/**
 * Widget wrapper for the UserInfoDisplay component.
 */
export class UserInfoDisplayWidget extends ReactWidget {
  private _notebookPanel: NotebookPanel;

  constructor(notebookPanel: NotebookPanel) {
    super();
    this._notebookPanel = notebookPanel;
    this.addClass('git-lock-sign-user-info-widget');
  }

  protected render(): JSX.Element {
    return (
      <UserInfoDisplayComponent
        notebookPanel={this._notebookPanel}
      />
    );
  }
}
