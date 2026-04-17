import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { observabilityApi } from "../../apis/observability";

const createTableThunk = (type, request) =>
  createAsyncThunk(type, async (tableName, { rejectWithValue }) => {
    try {
      const response = await request(tableName);
      return { tableName, data: response.data };
    } catch (error) {
      return rejectWithValue({
        tableName,
        message: error.response?.data?.detail || "Could not load observability data.",
      });
    }
  });

export const fetchSnapshots = createTableThunk("observability/fetchSnapshots", observabilityApi.getSnapshots);
export const fetchVolumeTS = createTableThunk("observability/fetchVolumeTS", observabilityApi.getVolumeTS);
export const fetchIncidents = createTableThunk("observability/fetchIncidents", observabilityApi.getIncidents);
export const fetchSchema = createTableThunk("observability/fetchSchema", observabilityApi.getSchema);
export const fetchColumnStats = createTableThunk("observability/fetchColumnStats", observabilityApi.getColumnStats);

const initialState = {
  snapshotsByTable: {},
  volumeTSByTable: {},
  incidentsByTable: {},
  schemasByTable: {},
  columnStatsByTable: {},
  loading: false,
  statusByTable: {},
  errorByTable: {},
};

const setPending = (state, action) => {
  const tableName = action.meta.arg;
  state.loading = true;
  state.statusByTable[tableName] = "loading";
  state.errorByTable[tableName] = null;
};

const setFulfilled = (state, action, targetKey) => {
  const { tableName, data } = action.payload;
  state.statusByTable[tableName] = "succeeded";
  state[targetKey][tableName] = data;
  state.loading = Object.values(state.statusByTable).some((status) => status === "loading");
};

const setRejected = (state, action) => {
  const tableName = action.payload?.tableName || action.meta.arg;
  state.loading = false;
  state.statusByTable[tableName] = "failed";
  state.errorByTable[tableName] = action.payload?.message || "Could not load observability data.";
};

const observabilitySlice = createSlice({
  name: "observability",
  initialState,
  reducers: {
    clearCache: (state) => {
      state.snapshotsByTable = {};
      state.volumeTSByTable = {};
      state.incidentsByTable = {};
      state.schemasByTable = {};
      state.columnStatsByTable = {};
      state.statusByTable = {};
      state.errorByTable = {};
      state.loading = false;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchSnapshots.pending, setPending)
      .addCase(fetchSnapshots.fulfilled, (state, action) => {
        setFulfilled(state, action, "snapshotsByTable");
      })
      .addCase(fetchSnapshots.rejected, setRejected)
      .addCase(fetchVolumeTS.pending, setPending)
      .addCase(fetchVolumeTS.fulfilled, (state, action) => {
        setFulfilled(state, action, "volumeTSByTable");
      })
      .addCase(fetchVolumeTS.rejected, setRejected)
      .addCase(fetchIncidents.pending, setPending)
      .addCase(fetchIncidents.fulfilled, (state, action) => {
        setFulfilled(state, action, "incidentsByTable");
      })
      .addCase(fetchIncidents.rejected, setRejected)
      .addCase(fetchSchema.pending, setPending)
      .addCase(fetchSchema.fulfilled, (state, action) => {
        setFulfilled(state, action, "schemasByTable");
      })
      .addCase(fetchSchema.rejected, setRejected)
      .addCase(fetchColumnStats.pending, setPending)
      .addCase(fetchColumnStats.fulfilled, (state, action) => {
        setFulfilled(state, action, "columnStatsByTable");
      })
      .addCase(fetchColumnStats.rejected, setRejected);
  },
});

export const { clearCache } = observabilitySlice.actions;
export default observabilitySlice.reducer;
