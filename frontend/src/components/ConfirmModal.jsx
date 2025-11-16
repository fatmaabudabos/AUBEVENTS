import { useEffect } from 'react';
import './ConfirmModal.css';

function ConfirmModal({
    isOpen,
    title,
    description,
    confirmLabel = 'Confirm',
    cancelLabel = 'Cancel',
    tone = 'default',
    onConfirm,
    onCancel,
    onClose,
}) {
    useEffect(() => {
        if (!isOpen) return undefined;

        const handleKeyDown = (event) => {
            if (event.key === 'Escape') {
                event.preventDefault();
                if (typeof onClose === 'function') {
                    onClose();
                }
            }
        };

        document.addEventListener('keydown', handleKeyDown);
        return () => {
            document.removeEventListener('keydown', handleKeyDown);
        };
    }, [isOpen, onClose]);

    if (!isOpen) return null;

    const handleOverlayClick = (event) => {
        if (event.target === event.currentTarget && typeof onClose === 'function') {
            onClose();
        }
    };

    const confirmButtonClass = tone === 'danger' ? 'btn btn-danger' : 'btn btn-primary';

    return (
        <div
            className="confirm-modal-overlay"
            role="dialog"
            aria-modal="true"
            aria-labelledby="confirm-modal-title"
            onClick={handleOverlayClick}
        >
            <div className={`confirm-modal-card ${tone === 'danger' ? 'confirm-modal-card-danger' : ''}`}>
                <button
                    type="button"
                    className="confirm-modal-close"
                    onClick={onClose}
                    aria-label="Close dialog"
                >
                    ×
                </button>
                {title && (
                    <h3 id="confirm-modal-title" className="confirm-modal-title">
                        {title}
                    </h3>
                )}
                {description && (
                    <p className="confirm-modal-description">{description}</p>
                )}
                <div className="confirm-modal-actions">
                    <button type="button" className="btn btn-secondary" onClick={onCancel || onClose}>
                        {cancelLabel}
                    </button>
                    <button type="button" className={confirmButtonClass} onClick={onConfirm}>
                        {confirmLabel}
                    </button>
                </div>
            </div>
        </div>
    );
}

export default ConfirmModal;
