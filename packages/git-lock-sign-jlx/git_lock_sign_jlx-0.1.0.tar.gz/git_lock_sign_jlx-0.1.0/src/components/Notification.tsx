import * as React from 'react';
import { gitLockSignAPI } from '../services/api';

interface INotificationProps {
  message: string;
  type: 'success' | 'error' | 'info';
  onDismiss: () => void;
}

export const Notification: React.FC<INotificationProps> = ({ message, type, onDismiss }) => {
  const [visible, setVisible] = React.useState(true);

  React.useEffect(() => {
    const setupTimer = async () => {
      const timeoutMs = await gitLockSignAPI.getNotificationTimeout();
      const timer = setTimeout(() => {
        handleDismiss();
      }, timeoutMs);

      return () => clearTimeout(timer);
    };

    setupTimer();
  }, []);

  const handleDismiss = () => {
    setVisible(false);
    onDismiss();
  };

  if (!visible) {
    return null;
  }

  return (
    <div className={`git-lock-sign-notification ${type}`}>
      <p>{message}</p>
      <button onClick={handleDismiss} className="dismiss-button">
        &times;
      </button>
    </div>
  );
};
