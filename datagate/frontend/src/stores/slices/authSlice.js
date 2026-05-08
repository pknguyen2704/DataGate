import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { authApi } from "~/apis/authApi";

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

export const logout = createAsyncThunk(
  "auth/logout",
  async (_, { rejectWithValue }) => {
    try {
      await authApi.logout();
    } catch (err) {
      console.error("Logout API failed", err);
    } finally {
      clearStoredToken();
    }
  }
);

export const changePassword = createAsyncThunk(
  "auth/changePassword",
  async (data, { rejectWithValue }) => {
    try {
      const res = await authApi.changePassword(data);
      return res.data;
    } catch (err) {
      return rejectWithValue(
        err.response?.data?.detail || "Change password failed"
      );
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
    } catch (error) {
      clearStoredToken();
      return rejectWithValue(error.response?.data?.detail || "Auth initialization failed");
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
      })
      // Logout
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
        state.loading = false;
        state.status = "idle";
        state.error = null;
      })
      // Change Password
      .addCase(changePassword.pending, (state) => {
        state.loading = true;
        state.status = "loading";
      })
      .addCase(changePassword.fulfilled, (state) => {
        state.loading = false;
        state.status = "success";
      })
      .addCase(changePassword.rejected, (state, action) => {
        state.loading = false;
        state.status = "error";
        state.error = action.payload;
      });

  },
});

export const { clearError } = authSlice.actions;

export default authSlice.reducer;
