import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider } from '@mui/material/styles'
import { ConfirmProvider } from 'material-ui-confirm'
import { CssBaseline } from '@mui/material'
import { ToastContainer } from 'react-toastify'
import { Provider } from 'react-redux'
import theme from '~/theme'
import { store } from '~/stores'
import App from '~/App.jsx'

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
        <App />
        <ToastContainer
          position="bottom-right"
          autoClose={4000}
          hideProgressBar
          newestOnTop
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
          theme="colored"
        />
      </ConfirmProvider>
    </ThemeProvider>
  </BrowserRouter>
  </Provider>
)
