import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import * as Sentry from '@sentry/react'
import './index.css'
import App from './App.jsx'

const sentryDsn = import.meta.env.VITE_SENTRY_DSN
if (sentryDsn) {
  Sentry.init({
    dsn: sentryDsn,
    integrations: [Sentry.browserTracingIntegration()],
    tracesSampleRate: 0.0,
  })

  if (typeof window !== 'undefined' && !window.__sentryButtonBreadcrumbListener) {
    const handler = (event) => {
      const button = event.target.closest('button')
      if (!button) return

      const label = (button.getAttribute('aria-label') || button.textContent || '').trim()
      if (!label) return

      Sentry.addBreadcrumb({
        category: 'ui.click',
        message: label,
        data: {
          id: button.id || undefined,
          class: button.className || undefined,
        },
        level: 'info',
      })
    }

    window.addEventListener('click', handler, { capture: true })
    window.__sentryButtonBreadcrumbListener = handler
  }
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Sentry.ErrorBoundary fallback={<p>Something went wrong.</p>}>
      <App />
    </Sentry.ErrorBoundary>
  </StrictMode>,
)