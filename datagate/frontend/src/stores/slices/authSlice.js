import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { authApi } from "~/apis/authApi";

const TOKEN_KEY = "token";

const readToken = () => localStorage.getItem(TOKEN_KEY);
const storeToken = (token) => localStorage.setItem(TOKEN_KEY, token);
const removeToken = () => localStorage.removeItem(TOKEN_KEY);

const getErrorMessage = (error, fallbackMessage) => (
  error.response?.data?.detail || fallbackMessage
);

const markAsLoading = (state) => {
  state.loading = true;
  state.status = "loading";
  state.error = null;
};

const markAsLoggedIn = (state, payload) => {
  state.loading = false;
  state.status = "authenticated";
  state.isAuthenticated = true;
  state.user = payload.user;
  state.token = payload.token;
  state.error = null;
};

const markAsLoggedOut = (state, status = "anonymous") => {
  state.loading = false;
  state.status = status;
  state.isAuthenticated = false;
  state.user = null;
  state.token = null;
};

export const login = createAsyncThunk(
  "auth/login",
  async (loginData, { rejectWithValue }) => {
    try {
      const response = await authApi.login(loginData);
      const token = response.data.access_token;

      storeToken(token);

      return {
        user: response.data.user,
        token,
      };
    } catch (error) {
      removeToken();
      return rejectWithValue(getErrorMessage(error, "Login failed"));
    }
  }
);

export const logout = createAsyncThunk("auth/logout", async () => {
  try {
    await authApi.logout();
  } catch (error) {
    console.error("Logout API failed", error);
  } finally {
    removeToken();
  }
});

export const initializeAuth = createAsyncThunk(
  "auth/initialize",
  async (_, { rejectWithValue }) => {
    const token = readToken();

    if (!token) {
      return rejectWithValue("No token");
    }

    try {
      const response = await authApi.getMe();

      return {
        user: response.data,
        token,
      };
    } catch (error) {
      removeToken();
      return rejectWithValue(
        getErrorMessage(error, "Auth initialization failed")
      );
    }
  }
);

const savedToken = readToken();

const initialState = {
  user: null,
  token: savedToken,
  isAuthenticated: Boolean(savedToken),
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
      .addCase(login.pending, markAsLoading)
      .addCase(login.fulfilled, (state, action) => {
        markAsLoggedIn(state, action.payload);
      })
      .addCase(login.rejected, (state, action) => {
        markAsLoggedOut(state, "error");
        state.error = action.payload;
      })

      .addCase(initializeAuth.pending, markAsLoading)
      .addCase(initializeAuth.fulfilled, (state, action) => {
        markAsLoggedIn(state, action.payload);
      })
      .addCase(initializeAuth.rejected, (state) => {
        markAsLoggedOut(state);
      })

      .addCase(logout.fulfilled, (state) => {
        markAsLoggedOut(state, "idle");
        state.error = null;
      });
  },
});

export const { clearError } = authSlice.actions;

export default authSlice.reducer;
