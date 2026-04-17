import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { authApi } from "~/apis/auth";

const TOKEN_KEY = "token";

const getStoredToken = () => localStorage.getItem(TOKEN_KEY);
const saveToken = (token) => localStorage.setItem(TOKEN_KEY, token);
const clearStoredToken = () => localStorage.removeItem(TOKEN_KEY);

export const login = createAsyncThunk(
  "auth/login",
  async ({ username, password }, { rejectWithValue }) => {
    try {
      const res = await authApi.login(username, password);
      const accessToken = res.data.access_token;
      saveToken(accessToken);

      const meRes = await authApi.getMe();
      return {
        user: meRes.data,
        token: accessToken,
      };
    } catch (err) {
      clearStoredToken();
      return rejectWithValue(err.response?.data?.detail || "Login failed");
    }
  }
);

export const initializeAuth = createAsyncThunk(
  "auth/initialize",
  async (_, { rejectWithValue }) => {
    const token = getStoredToken();
    if (!token) return rejectWithValue("No token");

    try {
      const meRes = await authApi.getMe();
      return {
        user: meRes.data,
        token,
      };
    } catch (err) {
      clearStoredToken();
      return rejectWithValue("Auth initialization failed");
    }
  }
);

const initialState = {
  user: null,
  token: getStoredToken(),
  isAuthenticated: Boolean(getStoredToken()),
  loading: true,
  status: "idle",
  error: null,
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    logout: (state) => {
      clearStoredToken();
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
      state.loading = false;
      state.status = "idle";
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
        state.status = "loading";
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.status = "authenticated";
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.token = action.payload.token;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.status = "error";
        state.isAuthenticated = false;
        state.error = action.payload;
      })
      // Initialize Auth
      .addCase(initializeAuth.pending, (state) => {
        state.loading = true;
        state.status = "loading";
      })
      .addCase(initializeAuth.fulfilled, (state, action) => {
        state.loading = false;
        state.status = "authenticated";
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.token = action.payload.token;
      })
      .addCase(initializeAuth.rejected, (state) => {
        state.loading = false;
        state.status = "anonymous";
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
      });
  },
});

export const { logout, clearError } = authSlice.actions;
export default authSlice.reducer;
