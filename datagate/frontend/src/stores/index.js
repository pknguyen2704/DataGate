import { configureStore } from '@reduxjs/toolkit';
import observabilityReducer from './slices/observabilitySlice';
import authReducer from './slices/authSlice';
import servicesReducer from './slices/servicesSlice';
import monitoringReducer from './slices/monitoringSlice';

export const store = configureStore({
  reducer: {
    observability: observabilityReducer,
    auth: authReducer,
    services: servicesReducer,
    monitoring: monitoringReducer,
  },
});
