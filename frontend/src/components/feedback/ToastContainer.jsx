const STYLES = {
  success: { bg: '#2e7d32', icon: '✓' },
  error: { bg: '#c62828', icon: '✕' },
  warning: { bg: '#ed6c02', icon: '!' },
  info: { bg: '#0288d1', icon: 'i' }
}

export default function ToastContainer({ toasts, onDismiss }) {
  if (toasts.length === 0) return null

  return (
    <div style={{
      position: 'fixed',
      top: '90px',
      right: '20px',
      zIndex: 99999,
      display: 'flex',
      flexDirection: 'column',
      gap: '10px',
      maxWidth: '380px'
    }}>
      {toasts.map(toast => {
        const style = STYLES[toast.type] || STYLES.info
        return (
          <div
            key={toast.id}
            style={{
              background: '#fff',
              borderLeft: `5px solid ${style.bg}`,
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
              borderRadius: '8px',
              padding: '14px 16px',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '12px',
              animation: 'slideIn 0.3s ease'
            }}
          >
            <span style={{
              background: style.bg,
              color: '#fff',
              borderRadius: '50%',
              width: '22px',
              height: '22px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '13px',
              fontWeight: 'bold',
              flexShrink: 0
            }}>{style.icon}</span>
            <span style={{ flex: 1, color: '#333', fontSize: '14px', lineHeight: '1.4' }}>{toast.message}</span>
            <button
              onClick={() => onDismiss(toast.id)}
              style={{
                background: 'transparent',
                border: 'none',
                cursor: 'pointer',
                color: '#999',
                fontSize: '18px',
                lineHeight: 1,
                padding: 0
              }}
            >&times;</button>
          </div>
        )
      })}
      <style>{`@keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }`}</style>
    </div>
  )
}