import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { observabilityApi } from "~/apis/observability";
import { getErrorMessage } from "~/utils/errorUtils";

export const fetchSnapshots = createAsyncThunk(
  "observability/fetchSnapshots",
  async ({ tableName, schemaName }, { rejectWithValue }) => {
    try {
      const response = await observabilityApi.getSnapshots({
        table: tableName,
        schema: schemaName || null,
      });
      const key = `${schemaName || 'public'}.${tableName}`;
      return { tableName: key, data: response.data };
    } catch (error) {
      return rejectWithValue({
        tableName: `${schemaName || 'public'}.${tableName}`,
        message: getErrorMessage(error, "Could not load snapshots."),
      });
    }
  }
);

export const fetchVolumeTS = createAsyncThunk(
  "observability/fetchVolumeTS",
  async ({ tableName, schemaName }, { rejectWithValue }) => {
    try {
      const response = await observabilityApi.getVolumeTS({
        table: tableName,
        schema: schemaName || null,
      });
      const key = `${schemaName || 'public'}.${tableName}`;
      return { tableName: key, data: response.data };
    } catch (error) {
      return rejectWithValue({
        tableName: `${schemaName || 'public'}.${tableName}`,
        message: getErrorMessage(error, "Could not load volume TS."),
      });
    }
  }
);

export const fetchSchema = createAsyncThunk(
  "observability/fetchSchema",
  async ({ tableName, schemaName }, { rejectWithValue }) => {
    try {
      const response = await observabilityApi.getSchema({
        table: tableName,
        schema: schemaName || null,
      });
      const key = `${schemaName || 'public'}.${tableName}`;
      return { tableName: key, data: response.data };
    } catch (error) {
      return rejectWithValue({
        tableName: `${schemaName || 'public'}.${tableName}`,
        message: getErrorMessage(error, "Could not load schema."),
      });
    }
  }
);

export const fetchIncidents = createAsyncThunk(
  "observability/fetchIncidents",
  async ({ tableName, schemaName }, { rejectWithValue }) => {
    try {
      const response = await observabilityApi.getIncidents({
        table: tableName,
        schema: schemaName || null,
      });
      const key = `${schemaName || 'public'}.${tableName}`;
      return { tableName: key, data: response.data };
    } catch (error) {
      return rejectWithValue({
        tableName: `${schemaName || 'public'}.${tableName}`,
        message: getErrorMessage(error, "Could not load incidents."),
      });
    }
  }
);

export const fetchVolumePrediction = createAsyncThunk(
  "observability/fetchVolumePrediction",
  async ({ tableName, schemaName }, { rejectWithValue }) => {
    try {
      const response = await observabilityApi.getVolumePrediction({
        table: tableName,
        schema: schemaName || null,
      });
      const key = `${schemaName || 'public'}.${tableName}`;
      return { tableName: key, data: response.data };
    } catch (error) {
      return rejectWithValue({
        tableName: `${schemaName || 'public'}.${tableName}`,
        message: getErrorMessage(error, "Could not load volume prediction."),
      });
    }
  }
);

export const fetchFreshnessPrediction = createAsyncThunk(
  "observability/fetchFreshnessPrediction",
  async ({ tableName, schemaName }, { rejectWithValue }) => {
    try {
      const response = await observabilityApi.getFreshnessPrediction({
        table: tableName,
        schema: schemaName || null,
      });
      const key = `${schemaName || 'public'}.${tableName}`;
      return { tableName: key, data: response.data };
    } catch (error) {
      return rejectWithValue({
        tableName: `${schemaName || 'public'}.${tableName}`,
        message: getErrorMessage(error, "Could not load freshness prediction."),
      });
    }
  }
);

export const fetchSchemaHistory = createAsyncThunk(
  "observability/fetchSchemaHistory",
  async ({ tableName, schemaName }, { rejectWithValue }) => {
    try {
      const response = await observabilityApi.getSchemaHistory({
        table: tableName,
        schema: schemaName || null,
      });
      const key = `${schemaName || 'public'}.${tableName}`;
      return { tableName: key, data: response.data };
    } catch (error) {
      return rejectWithValue({
        tableName: `${schemaName || 'public'}.${tableName}`,
        message: getErrorMessage(error, "Could not load schema history."),
      });
    }
  }
);

export const fetchMetrics = createAsyncThunk(
  "observability/fetchMetrics",
  async ({ tableName, schemaName, column }, { rejectWithValue }) => {
    try {
      const response = await observabilityApi.getMetrics({
        table: tableName,
        schema: schemaName || null,
        column: column || null,
      });
      const key = `${schemaName || 'public'}.${tableName}`;
      return { tableName: key, data: response.data };
    } catch (error) {
      return rejectWithValue({
        tableName: `${schemaName || 'public'}.${tableName}`,
        message: getErrorMessage(error, "Could not load metrics."),
      });
    }
  }
);

export const resolveIncident = createAsyncThunk(
  "observability/resolveIncident",
  async ({ incidentId, tableName }, { rejectWithValue }) => {
    try {
      await observabilityApi.resolveIncident(incidentId);
      return { incidentId, tableName };
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not resolve incident."));
    }
  }
);

const initialState = {
  snapshotsByTable: {},
  volumeTSByTable: {},
  schemasByTable: {},
  incidentsByTable: {},
  metricsByTable: {},
  metricsStatusByTable: {},
  volumePredictionByTable: {},
  freshnessPredictionByTable: {},
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
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchSnapshots.fulfilled, (state, action) => {
        const { tableName, data } = action.payload;
        state.snapshotsByTable[tableName] = data;
      })
      .addCase(fetchVolumeTS.fulfilled, (state, action) => {
        const { tableName, data } = action.payload;
        state.volumeTSByTable[tableName] = data;
      })
      .addCase(fetchSchema.fulfilled, (state, action) => {
        const { tableName, data } = action.payload;
        state.schemasByTable[tableName] = data;
      })
      .addCase(fetchIncidents.fulfilled, (state, action) => {
        const { tableName, data } = action.payload;
        state.incidentsByTable[tableName] = data;
      })
      .addCase(fetchVolumePrediction.fulfilled, (state, action) => {
        const { tableName, data } = action.payload;
        state.volumePredictionByTable[tableName] = data;
      })
      .addCase(fetchFreshnessPrediction.fulfilled, (state, action) => {
        const { tableName, data } = action.payload;
        state.freshnessPredictionByTable[tableName] = data;
      })
      .addCase(fetchSchemaHistory.fulfilled, (state, action) => {
        const { tableName, data } = action.payload;
        state.schemaHistoryByTable[tableName] = data;
      })
      .addCase(fetchMetrics.pending, (state, action) => {
        const { tableName } = action.meta.arg;
        const key = `${action.meta.arg.schemaName || 'public'}.${tableName}`;
        state.metricsStatusByTable[key] = "loading";
      })
      .addCase(fetchMetrics.fulfilled, (state, action) => {
        const { tableName, data } = action.payload;
        state.metricsByTable[tableName] = data;
        state.metricsStatusByTable[tableName] = "succeeded";
      })
      .addCase(fetchMetrics.rejected, (state, action) => {
        const { tableName } = action.payload || {};
        if (tableName) {
          state.metricsStatusByTable[tableName] = "failed";
        }
      })
      .addCase(resolveIncident.fulfilled, (state, action) => {
        const { incidentId, tableName } = action.payload;
        const incidents = state.incidentsByTable[tableName];
        if (incidents) {
          state.incidentsByTable[tableName] = incidents.map(inc =>
            inc.id === incidentId ? { ...inc, status: "resolved" } : inc
          );
        }
      });
  },
});

export const { clearObservabilityCache } = observabilitySlice.actions;
export default observabilitySlice.reducer;
