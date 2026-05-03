import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice/authSlice';
import exploreReducer from './slices/tableSlice/index';
import connectionReducer from './slices/connectionSlice/connectionSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    explore: exploreReducer,
    connection: connectionReducer,
  },
});
