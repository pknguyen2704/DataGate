import { configureStore } from '@reduxjs/toolkit';
import observabilityReducer from './slices/observabilitySlice';
import authReducer from './slices/authSlice';

export const store = configureStore({
  reducer: {
    observability: observabilityReducer,
    auth: authReducer,
  },
});
