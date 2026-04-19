import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { servicesApi } from "~/apis/services";
import { usersApi } from "~/apis/users";
import { observabilityApi } from "~/apis/observability";

const getErrorMessage = (error, fallback) =>
  error.response?.data?.detail || error.message || fallback;

// --- 1. SERVICE MANAGEMENT ---

export const createService = createAsyncThunk(
  "settings/createService",
  async (payload, { rejectWithValue }) => {
    try {
      const response = await servicesApi.createService(payload);
      return response.data;
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not create service."));
    }
  }
);

export const updateService = createAsyncThunk(
  "settings/updateService",
  async ({ serviceId, data }, { rejectWithValue }) => {
    try {
      const response = await servicesApi.updateService(serviceId, data);
      return response.data;
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not update service."));
    }
  }
);

export const deleteService = createAsyncThunk(
  "settings/deleteService",
  async (serviceId, { rejectWithValue }) => {
    try {
      await servicesApi.deleteService(serviceId);
      return serviceId;
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not delete service."));
    }
  }
);

export const testServiceConnection = createAsyncThunk(
  "settings/testServiceConnection",
  async (payload, { rejectWithValue }) => {
    try {
      const response = await servicesApi.testConnection(payload);
      return response.data;
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Connection test failed."));
    }
  }
);

export const refreshServiceTables = createAsyncThunk(
  "settings/refreshServiceTables",
  async (serviceId, { rejectWithValue }) => {
    try {
      await observabilityApi.refreshTables(serviceId);
      return serviceId;
    } catch (error) {
      return rejectWithValue({
        serviceId,
        message: getErrorMessage(error, "Could not refresh service tables."),
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
  
  refreshingByService: {},
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
      // Service Mutations
      .addCase(createService.pending, (state) => {
        state.mutationStatus = "loading";
      })
      .addCase(createService.fulfilled, (state) => {
        state.mutationStatus = "succeeded";
      })
      .addCase(createService.rejected, (state, action) => {
        state.mutationStatus = "failed";
        state.mutationError = action.payload;
      })
      
      // Connection Test
      .addCase(testServiceConnection.pending, (state) => {
        state.testConnectionStatus = "loading";
      })
      .addCase(testServiceConnection.fulfilled, (state, action) => {
        state.testConnectionStatus = "succeeded";
        state.testConnectionResult = action.payload;
      })
      
      // Users
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.usersStatus = "succeeded";
        state.users = action.payload;
      })
      
      // Refresh Service Tables
      .addCase(refreshServiceTables.pending, (state, action) => {
        state.refreshingByService[action.meta.arg] = true;
      })
      .addCase(refreshServiceTables.fulfilled, (state, action) => {
        state.refreshingByService[action.payload] = false;
      })
      .addCase(refreshServiceTables.rejected, (state, action) => {
        const serviceId = action.meta.arg;
        state.refreshingByService[serviceId] = false;
      });
  },
});

export const { resetMutationState, resetTestConnection } = settingsSlice.actions;
export default settingsSlice.reducer;
