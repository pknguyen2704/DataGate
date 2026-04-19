import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import exploreReducer from './slices/exploreSlice/index';
import settingsReducer from './slices/settingsSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    explore: exploreReducer,
    settings: settingsReducer,
  },
});
