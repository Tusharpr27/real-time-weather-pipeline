import React from 'react'
import ReactDOM from 'react-dom/client'
import { Provider } from 'react-redux'
import App from './App.tsx'
import store from './store'
import './styles/global.css'
// import { registerServiceWorker } from '@/utils/registerServiceWorker'

// Register Service Worker for offline support
// registerServiceWorker()

// Log connectivity status
if (!navigator.onLine) {
  console.log('[PWA] App loaded offline')
}

// Global error overlay to surface runtime errors (helps debug blank white screen)
function showErrorOverlay(title: string, message?: string) {
  const id = 'global-error-overlay'
  let el = document.getElementById(id)
  if (!el) {
    el = document.createElement('div')
    el.id = id
    Object.assign(el.style, {
      position: 'fixed',
      left: '0',
      top: '0',
      right: '0',
      bottom: '0',
      background: 'rgba(30, 41, 59, 0.95)',
      color: '#fff',
      zIndex: '999999',
      padding: '24px',
      fontFamily: 'monospace',
      overflow: 'auto',
    })
    document.body.appendChild(el)
  }
  el.innerHTML = `<div style="max-width:1000px;margin:48px auto;background:#111827;padding:20px;border-radius:8px;border:1px solid rgba(255,255,255,0.06)">
    <h2 style="margin:0 0 8px;color:#ff6b6b">${title}</h2>
    <pre style="white-space:pre-wrap;font-size:13px;line-height:1.4;color:#f8fafc">${message || ''}</pre>
    <div style="margin-top:12px;color:#9ca3af">Refresh the page after addressing the error. Close this overlay by calling <code>document.getElementById('${id}').remove()</code> in the console.</div>
  </div>`
}

window.addEventListener('error', (ev) => {
  try {
    const err = ev.error || ev.message || String(ev)
    console.error('Global error caught:', ev)
    showErrorOverlay('Runtime Error', String(err))
  } catch (e) {
    console.error('Failed to render error overlay', e)
  }
})

window.addEventListener('unhandledrejection', (ev) => {
  try {
    const reason = (ev.reason && (ev.reason.stack || ev.reason.message || JSON.stringify(ev.reason))) || String(ev.reason)
    console.error('Unhandled promise rejection:', ev)
    showErrorOverlay('Unhandled Promise Rejection', reason)
  } catch (e) {
    console.error('Failed to render rejection overlay', e)
  }
})

// Unregister any existing service workers to avoid serving stale cached app shell
if ('serviceWorker' in navigator) {
  navigator.serviceWorker
    .getRegistrations()
    .then((regs) => {
      regs.forEach((r) => r.unregister())
      if (regs.length > 0) console.log('[PWA] Unregistered existing service workers')
    })
    .catch((e) => console.warn('[PWA] Failed to unregister service workers', e))
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>,
)

// Wrap mount in try/catch to surface synchronous errors during render
try {
  console.log('[APP] Mounting React app')
} catch (err) {
  console.error('[APP] Error during mount', err)
  showErrorOverlay('Render Error', String(err))
}
