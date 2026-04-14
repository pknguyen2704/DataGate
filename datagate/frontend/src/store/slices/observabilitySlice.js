import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { observabilityApi } from '../../apis/observability';

export const fetchSnapshots = createAsyncThunk(
  'observability/fetchSnapshots',
  async (tableName) => {
    const response = await observabilityApi.getSnapshots(tableName);
    return { tableName, data: response.data };
  }
);

export const fetchVolumeTS = createAsyncThunk(
  'observability/fetchVolumeTS',
  async (tableName) => {
    const response = await observabilityApi.getVolumeTS(tableName);
    return { tableName, data: response.data };
  }
);

export const fetchIncidents = createAsyncThunk(
  'observability/fetchIncidents',
  async (tableName) => {
    const response = await observabilityApi.getIncidents(tableName);
    return { tableName, data: response.data };
  }
);

export const fetchSchema = createAsyncThunk(
  'observability/fetchSchema',
  async (tableName) => {
    const response = await observabilityApi.getSchema(tableName);
    return { tableName, data: response.data };
  }
);

export const fetchColumnStats = createAsyncThunk(
  'observability/fetchColumnStats',
  async (tableName) => {
    const response = await observabilityApi.getColumnStats(tableName);
    return { tableName, data: response.data };
  }
);

const observabilitySlice = createSlice({
  name: 'observability',
  initialState: {
    snapshotsByTable: {},
    volumeTSByTable: {},
    incidentsByTable: {},
    schemasByTable: {},
    columnStatsByTable: {},
    loading: false,
    error: null,
  },
  reducers: {
    clearCache: (state) => {
      state.snapshotsByTable = {};
      state.volumeTSByTable = {};
      state.incidentsByTable = {};
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchSnapshots.pending, (state) => { state.loading = true; })
      .addCase(fetchSnapshots.fulfilled, (state, action) => {
        state.loading = false;
        state.snapshotsByTable[action.payload.tableName] = action.payload.data;
      })
      .addCase(fetchVolumeTS.fulfilled, (state, action) => {
        state.volumeTSByTable[action.payload.tableName] = action.payload.data;
      })
      .addCase(fetchIncidents.fulfilled, (state, action) => {
        state.incidentsByTable[action.payload.tableName] = action.payload.data;
      })
      .addCase(fetchSchema.fulfilled, (state, action) => {
        state.schemasByTable[action.payload.tableName] = action.payload.data;
      })
      .addCase(fetchColumnStats.fulfilled, (state, action) => {
        state.columnStatsByTable[action.payload.tableName] = action.payload.data;
      });
  },
});

export const { clearCache } = observabilitySlice.actions;
export default observabilitySlice.reducer;
