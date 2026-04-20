import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { connectionsApi } from "~/apis/connections";
import { usersApi } from "~/apis/users";
import { observabilityApi } from "~/apis/observability";

const getErrorMessage = (error, fallback) =>
  error.response?.data?.detail || error.message || fallback;

// --- 1. CONNECTION MANAGEMENT ---

export const createConnection = createAsyncThunk(
  "settings/createConnection",
  async (payload, { rejectWithValue }) => {
    try {
      const response = await connectionsApi.createConnection(payload);
      return response.data;
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not create connection."));
    }
  }
);

export const updateConnection = createAsyncThunk(
  "settings/updateConnection",
  async ({ connectionId, data }, { rejectWithValue }) => {
    try {
      const response = await connectionsApi.updateConnection(connectionId, data);
      return response.data;
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not update connection."));
    }
  }
);

export const deleteConnection = createAsyncThunk(
  "settings/deleteConnection",
  async (connectionId, { rejectWithValue }) => {
    try {
      await connectionsApi.deleteConnection(connectionId);
      return connectionId;
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not delete connection."));
    }
  }
);

export const testConnection = createAsyncThunk(
  "settings/testConnection",
  async (payload, { rejectWithValue }) => {
    try {
      const response = await connectionsApi.testConnection(payload);
      return response.data;
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Connection test failed."));
    }
  }
);

export const refreshConnectionTables = createAsyncThunk(
  "settings/refreshConnectionTables",
  async (connectionId, { rejectWithValue }) => {
    try {
      // Logic for refreshing table metadata, possibly via observability sync
      await observabilityApi.triggerScan({ connection_id: connectionId }); 
      return connectionId;
    } catch (error) {
      return rejectWithValue({
        connectionId,
        message: getErrorMessage(error, "Could not refresh connection tables."),
      });
    }
  }
);

// --- 2. USER MANAGEMENT ---

export const fetchUsers = createAsyncThunk(
  "settings/fetchUsers",
  async ({ skip, limit } = {}, { rejectWithValue }) => {
    try {
      const response = await usersApi.getUsers(skip, limit);
      return response.data || [];
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not load users."));
    }
  }
);

export const createUser = createAsyncThunk(
  "settings/createUser",
  async (data, { rejectWithValue }) => {
    try {
      const response = await usersApi.createUser(data);
      return response.data;
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not create user."));
    }
  }
);

const initialState = {
  users: [],
  usersStatus: "idle",
  usersError: null,
  
  mutationStatus: "idle",
  mutationError: null,
  
  testConnectionResult: null,
  testConnectionStatus: "idle",
  
  refreshingByConnection: {},
};

const settingsSlice = createSlice({
  name: "settings",
  initialState,
  reducers: {
    resetMutationState: (state) => {
      state.mutationStatus = "idle";
      state.mutationError = null;
    },
    resetTestConnection: (state) => {
      state.testConnectionResult = null;
      state.testConnectionStatus = "idle";
    }
  },
  extraReducers: (builder) => {
    builder
      // Connection Mutations
      .addCase(createConnection.pending, (state) => {
        state.mutationStatus = "loading";
      })
      .addCase(createConnection.fulfilled, (state) => {
        state.mutationStatus = "succeeded";
      })
      .addCase(createConnection.rejected, (state, action) => {
        state.mutationStatus = "failed";
        state.mutationError = action.payload;
      })
      
      // Connection Test
      .addCase(testConnection.pending, (state) => {
        state.testConnectionStatus = "loading";
      })
      .addCase(testConnection.fulfilled, (state, action) => {
        state.testConnectionStatus = "succeeded";
        state.testConnectionResult = action.payload;
      })
      
      // Users
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.usersStatus = "succeeded";
        state.users = action.payload;
      })
      
      // Refresh Connection Tables
      .addCase(refreshConnectionTables.pending, (state, action) => {
        state.refreshingByConnection[action.meta.arg] = true;
      })
      .addCase(refreshConnectionTables.fulfilled, (state, action) => {
        state.refreshingByConnection[action.payload] = false;
      })
      .addCase(refreshConnectionTables.rejected, (state, action) => {
        const connectionId = action.meta.arg;
        state.refreshingByConnection[connectionId] = false;
      });
  },
});

export const { resetMutationState, resetTestConnection } = settingsSlice.actions;
export default settingsSlice.reducer;
