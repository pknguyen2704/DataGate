import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { observabilityApi } from "~/apis/observability";
import { getErrorMessage } from "~/utils/errorUtils";

const getTableKey = (schemaName, tableName) => `${schemaName || 'public'}.${tableName}`;

export const fetchSnapshots = createAsyncThunk(
  "observability/fetchSnapshots",
  async ({ tableName, schemaName }, { rejectWithValue }) => {
    try {
      const response = await observabilityApi.getSnapshots({ table: tableName, schema: schemaName || null });
      return { key: getTableKey(schemaName, tableName), data: response.data };
    } catch (error) {
      return rejectWithValue({ key: getTableKey(schemaName, tableName), message: getErrorMessage(error) });
    }
  }
);

export const fetchVolumeTS = createAsyncThunk(
  "observability/fetchVolumeTS",
  async ({ tableName, schemaName }, { rejectWithValue }) => {
    try {
      const response = await observabilityApi.getVolumeTS({ table: tableName, schema: schemaName || null });
      return { key: getTableKey(schemaName, tableName), data: response.data };
    } catch (error) {
      return rejectWithValue({ key: getTableKey(schemaName, tableName), message: getErrorMessage(error) });
    }
  }
);

export const fetchSchema = createAsyncThunk(
  "observability/fetchSchema",
  async ({ tableName, schemaName }, { rejectWithValue }) => {
    try {
      const response = await observabilityApi.getSchema({ table: tableName, schema: schemaName || null });
      return { key: getTableKey(schemaName, tableName), data: response.data };
    } catch (error) {
      return rejectWithValue({ key: getTableKey(schemaName, tableName), message: getErrorMessage(error) });
    }
  }
);

export const fetchIncidents = createAsyncThunk(
  "observability/fetchIncidents",
  async ({ tableName, schemaName }, { rejectWithValue }) => {
    try {
      const response = await observabilityApi.getIncidents({ table: tableName, schema: schemaName || null });
      return { key: getTableKey(schemaName, tableName), data: response.data };
    } catch (error) {
      return rejectWithValue({ key: getTableKey(schemaName, tableName), message: getErrorMessage(error) });
    }
  }
);

export const fetchVolumePrediction = createAsyncThunk(
  "observability/fetchVolumePrediction",
  async ({ tableName, schemaName }, { rejectWithValue }) => {
    try {
      const response = await observabilityApi.getVolumePrediction({ table: tableName, schema: schemaName || null });
      return { key: getTableKey(schemaName, tableName), data: response.data };
    } catch (error) {
      return rejectWithValue({ key: getTableKey(schemaName, tableName), message: getErrorMessage(error) });
    }
  }
);

export const fetchSchemaHistory = createAsyncThunk(
  "observability/fetchSchemaHistory",
  async ({ tableName, schemaName }, { rejectWithValue }) => {
    try {
      const response = await observabilityApi.getSchemaHistory({ table: tableName, schema: schemaName || null });
      return { key: getTableKey(schemaName, tableName), data: response.data };
    } catch (error) {
      return rejectWithValue({ key: getTableKey(schemaName, tableName), message: getErrorMessage(error) });
    }
  }
);

export const resolveIncident = createAsyncThunk(
  "observability/resolveIncident",
  async ({ incidentId, key }, { rejectWithValue }) => {
    try {
      await observabilityApi.resolveIncident(incidentId);
      return { incidentId, key };
    } catch (error) {
      return rejectWithValue(getErrorMessage(error));
    }
  }
);

const initialState = {
  snapshotsByTable: {},
  volumeTSByTable: {},
  schemasByTable: {},
  incidentsByTable: {},
  volumePredictionByTable: {},
  schemaHistoryByTable: {},
};

const observabilitySlice = createSlice({
  name: "observability",
  initialState,
  reducers: {
    clearObservabilityCache: (state) => {
      state.snapshotsByTable = {};
      state.volumeTSByTable = {};
      state.schemasByTable = {};
      state.incidentsByTable = {};
      state.volumePredictionByTable = {};
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchSnapshots.fulfilled, (state, action) => {
        state.snapshotsByTable[action.payload.key] = action.payload.data;
      })
      .addCase(fetchVolumeTS.fulfilled, (state, action) => {
        state.volumeTSByTable[action.payload.key] = action.payload.data;
      })
      .addCase(fetchSchema.fulfilled, (state, action) => {
        state.schemasByTable[action.payload.key] = action.payload.data;
      })
      .addCase(fetchIncidents.fulfilled, (state, action) => {
        state.incidentsByTable[action.payload.key] = action.payload.data;
      })
      .addCase(fetchVolumePrediction.fulfilled, (state, action) => {
        state.volumePredictionByTable[action.payload.key] = action.payload.data;
      })
      .addCase(fetchSchemaHistory.fulfilled, (state, action) => {
        state.schemaHistoryByTable[action.payload.key] = action.payload.data;
      })
      .addCase(resolveIncident.fulfilled, (state, action) => {
        const { incidentId, key } = action.payload;
        const incidents = state.incidentsByTable[key];
        if (incidents) {
          state.incidentsByTable[key] = incidents.map(inc =>
            inc.id === incidentId ? { ...inc, status: "resolved" } : inc
          );
        }
      });
  },
});

export const { clearObservabilityCache } = observabilitySlice.actions;
export default observabilitySlice.reducer;
