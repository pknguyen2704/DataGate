import { configureStore } from '@reduxjs/toolkit';
import observabilityReducer from './slices/observabilitySlice';

export const store = configureStore({
  reducer: {
    observability: observabilityReducer,
  },
});
