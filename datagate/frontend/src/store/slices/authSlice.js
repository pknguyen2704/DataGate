import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { authApi } from '../../apis/auth';

// Login then fetch full user profile
export const login = createAsyncThunk(
  'auth/login',
  async ({ username, password }, { rejectWithValue }) => {
    try {
      const res = await authApi.login(username, password);
      const accessToken = res.data.access_token;
      localStorage.setItem('token', accessToken);

      // Fetch real user profile from /auth/me
      const meRes = await authApi.getMe();
      return {
        user: meRes.data,
        token: accessToken,
      };
    } catch (err) {
      localStorage.removeItem('token');
      return rejectWithValue(err.response?.data?.detail || 'Login failed');
    }
  }
);

// On page reload — restore session by calling /auth/me with saved token
export const initializeAuth = createAsyncThunk(
  'auth/initialize',
  async (_, { rejectWithValue }) => {
    const token = localStorage.getItem('token');
    if (!token) return rejectWithValue('No token');

    try {
      const meRes = await authApi.getMe();
      return {
        user: meRes.data,
        token,
      };
    } catch (err) {
      localStorage.removeItem('token');
      return rejectWithValue('Auth initialization failed');
    }
  }
);

const initialState = {
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  loading: true,
  error: null,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout: (state) => {
      localStorage.removeItem('token');
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
      state.loading = false;
      state.error = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.token = action.payload.token;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Initialize Auth
      .addCase(initializeAuth.pending, (state) => {
        state.loading = true;
      })
      .addCase(initializeAuth.fulfilled, (state, action) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.token = action.payload.token;
      })
      .addCase(initializeAuth.rejected, (state) => {
        state.loading = false;
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
      });
  },
});

export const { logout, clearError } = authSlice.actions;
export default authSlice.reducer;
