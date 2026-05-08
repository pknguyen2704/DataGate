import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { connectionsApi, tablesApi } from "~/apis/api";

export const fetchConnections = createAsyncThunk("connection/list", async (params, { rejectWithValue }) => {
  try {
    const res = await connectionsApi.list(params);
    return res.data;
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const fetchConnection = createAsyncThunk("connection/get", async (id, { rejectWithValue }) => {
  try {
    const res = await connectionsApi.get(id);
    return res.data;
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const createConnection = createAsyncThunk("connection/create", async (data, { rejectWithValue }) => {
  try {
    const res = await connectionsApi.create(data);
    return res.data;
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const updateConnection = createAsyncThunk("connection/update", async ({ id, data }, { rejectWithValue }) => {
  try {
    const res = await connectionsApi.update(id, data);
    return res.data;
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const activateConnection = createAsyncThunk("connection/activate", async (id, { rejectWithValue }) => {
  try {
    const res = await connectionsApi.activate(id);
    return res.data;
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const disableConnection = createAsyncThunk("connection/disable", async (id, { rejectWithValue }) => {
  try {
    const res = await connectionsApi.deactivate(id);
    return res.data;
  } catch (err) {
    return rejectWithValue(err.message);
  }
});


export const deleteConnection = createAsyncThunk("connection/delete", async (id, { rejectWithValue }) => {
  try {
    await connectionsApi.delete(id);
    return id;
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const testConnection = createAsyncThunk("connection/test", async (id, { rejectWithValue }) => {
  try {
    const res = await connectionsApi.test(id);
    return res.data;
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const fetchCatalogs = createAsyncThunk("connection/catalogs", async (id, { rejectWithValue }) => {
  try {
    const res = await connectionsApi.listCatalogs(id);
    return res.data;
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const fetchSchemas = createAsyncThunk("connection/schemas", async (id, { rejectWithValue }) => {
  try {
    const res = await connectionsApi.listSchemas(id);
    return res.data;
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const fetchRemoteTables = createAsyncThunk("connection/remoteTables", async ({ id, params }, { rejectWithValue }) => {
  try {
    const res = await connectionsApi.listTables(id, params);
    return res.data;
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const fetchManagedTables = createAsyncThunk("connection/managedTables", async (id, { rejectWithValue }) => {
  try {
    const res = await connectionsApi.listManagedTables(id);
    return res.data;
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const addManagedTables = createAsyncThunk("connection/addManagedTables", async ({ id, catalog, schema, tableNames }, { dispatch, rejectWithValue }) => {
  try {
    const results = await Promise.allSettled(tableNames.map(name => tablesApi.create({
      connection_id: id, catalog_name: catalog, schema_name: schema, table_name: name,
    })));
    dispatch(fetchManagedTables(id));
    return {
      added: results.filter(r => r.status === "fulfilled").length,
      skipped: results.filter(r => r.status === "rejected").length,
    };
  } catch (err) {
    return rejectWithValue(err.message);
  }
});


const initialState = {
  connections: [],
  currentConnection: null,
  catalogs: [],
  schemas: [],
  remoteTables: [],
  managedTables: [],
  listStatus: "idle",
  detailStatus: "idle",
  mutationStatus: "idle",
  testStatus: "idle",
  discoveryStatus: "idle",
  managedTablesStatus: "idle",
  testResult: null,
  error: null,
};

const connectionSlice = createSlice({
  name: "connection",
  initialState,
  reducers: {
    clearError: (state) => { state.error = null; },
    resetConnectionMutation: (state) => { state.mutationStatus = "idle"; },
    resetConnectionTest: (state) => { state.testStatus = "idle"; state.testResult = null; },
    clearConnectionDetail: (state) => {
      state.currentConnection = null;
      state.catalogs = [];
      state.schemas = [];
      state.remoteTables = [];
      state.managedTables = [];
      state.detailStatus = "idle";
      state.discoveryStatus = "idle";
      state.managedTablesStatus = "idle";
      state.error = null;
      state.testResult = null;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchConnections.pending, (state) => { state.listStatus = "loading"; })
      .addCase(fetchConnections.fulfilled, (state, action) => { state.listStatus = "succeeded"; state.connections = action.payload; })
      .addCase(fetchConnection.pending, (state) => { state.detailStatus = "loading"; })
      .addCase(fetchConnection.fulfilled, (state, action) => { state.detailStatus = "succeeded"; state.currentConnection = action.payload; })
      .addCase(createConnection.pending, (state) => { state.mutationStatus = "loading"; })
      .addCase(createConnection.fulfilled, (state, action) => { state.mutationStatus = "succeeded"; state.connections.unshift(action.payload); })
      .addCase(updateConnection.pending, (state) => { state.mutationStatus = "loading"; })
      .addCase(updateConnection.fulfilled, (state, action) => {
        state.mutationStatus = "succeeded";
        state.currentConnection = action.payload;
        state.connections = state.connections.map(c => c.id === action.payload.id ? action.payload : c);
      })
      .addCase(activateConnection.fulfilled, (state, action) => {
        if (state.currentConnection?.id === action.payload.id) state.currentConnection = action.payload;
        state.connections = state.connections.map(c => c.id === action.payload.id ? action.payload : c);
      })
      .addCase(disableConnection.fulfilled, (state, action) => {
        if (state.currentConnection?.id === action.payload.id) state.currentConnection = action.payload;
        state.connections = state.connections.map(c => c.id === action.payload.id ? action.payload : c);
      })

      .addCase(deleteConnection.fulfilled, (state, action) => {
        state.connections = state.connections.filter(c => c.id !== action.payload);
      })
      .addCase(testConnection.pending, (state) => { state.testStatus = "loading"; })
      .addCase(testConnection.fulfilled, (state, action) => { state.testStatus = "succeeded"; state.testResult = action.payload; })
      .addCase(fetchCatalogs.pending, (state) => { state.discoveryStatus = "loading"; })
      .addCase(fetchCatalogs.fulfilled, (state, action) => { state.discoveryStatus = "succeeded"; state.catalogs = action.payload; })
      .addCase(fetchSchemas.pending, (state) => { state.discoveryStatus = "loading"; })
      .addCase(fetchSchemas.fulfilled, (state, action) => { state.discoveryStatus = "succeeded"; state.schemas = action.payload; })
      .addCase(fetchRemoteTables.pending, (state) => { state.discoveryStatus = "loading"; })
      .addCase(fetchRemoteTables.fulfilled, (state, action) => { state.discoveryStatus = "succeeded"; state.remoteTables = action.payload; })
      .addCase(fetchManagedTables.pending, (state) => { state.managedTablesStatus = "loading"; })
      .addCase(fetchManagedTables.fulfilled, (state, action) => { state.managedTablesStatus = "succeeded"; state.managedTables = action.payload; })
      .addMatcher(action => action.type.endsWith("/rejected"), (state, action) => {
        state.error = action.payload;
        if (state.listStatus === "loading") state.listStatus = "failed";
        if (state.detailStatus === "loading") state.detailStatus = "failed";
        if (state.mutationStatus === "loading") state.mutationStatus = "failed";
        if (state.testStatus === "loading") state.testStatus = "failed";
        if (state.discoveryStatus === "loading") state.discoveryStatus = "failed";
        if (state.managedTablesStatus === "loading") state.managedTablesStatus = "failed";
      });
  },
});

export const { clearError, resetConnectionMutation, resetConnectionTest, clearConnectionDetail } = connectionSlice.actions;
export default connectionSlice.reducer;
