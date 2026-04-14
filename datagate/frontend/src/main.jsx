import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider } from '@mui/material/styles'
import { ConfirmProvider } from 'material-ui-confirm'
import { CssBaseline } from '@mui/material'
import { ToastContainer } from 'react-toastify'
import theme from '~/theme'
import App from '~/App.jsx'
import { AuthProvider } from './contexts/AuthContext'
import './index.css'

import { Provider } from 'react-redux'
import { store } from './store'

createRoot(document.getElementById('root')).render(
  <Provider store={store}>
    <BrowserRouter basename="/">
    <ThemeProvider theme={theme}>
      <ConfirmProvider defaultOptions={{
        allowClose: false,
        dialogProps: {
          maxWidth: 'xs',
        },
        confirmationButtonProps: {
          color: 'secondary', 
          variant: 'outlined'
        },
        cancellationButtonProps: {
          color: 'inherit'
        },
      }}>
        <CssBaseline />
        <AuthProvider>
          <App />
        </AuthProvider>
        <ToastContainer position="bottom-right" theme="colored"/>
      </ConfirmProvider>
    </ThemeProvider>
  </BrowserRouter>
  </Provider>
)
