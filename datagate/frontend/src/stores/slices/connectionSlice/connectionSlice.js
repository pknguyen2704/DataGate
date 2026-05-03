import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import { connectionsApi, tablesApi } from "~/apis/api";

const getErrorMessage = (error, fallback) =>
  error.response?.data?.detail || error.response?.data?.message || error.message || fallback;

const isValidId = (id) => Boolean(id && id !== "undefined" && id !== "null");

export const fetchConnections = createAsyncThunk(
  "connection/fetchConnections",
  async (_, { rejectWithValue }) => {
    try {
      const response = await connectionsApi.list();
      return response.data || [];
    } catch (error) {
      if (error.response?.status === 404) return [];
      return rejectWithValue(getErrorMessage(error, "Could not load connections."));
    }
  },
);

export const fetchConnection = createAsyncThunk(
  "connection/fetchConnection",
  async (connectionId, { rejectWithValue }) => {
    try {
      if (!isValidId(connectionId)) return rejectWithValue("Invalid connection id.");
      const response = await connectionsApi.get(connectionId);
      return response.data;
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not load connection."));
    }
  },
);

export const createConnection = createAsyncThunk(
  "connection/createConnection",
  async (payload, { rejectWithValue }) => {
    try {
      const response = await connectionsApi.create(payload);
      return response.data;
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not create connection."));
    }
  },
);

export const updateConnection = createAsyncThunk(
  "connection/updateConnection",
  async ({ connectionId, data }, { rejectWithValue }) => {
    try {
      if (!isValidId(connectionId)) return rejectWithValue("Invalid connection id.");
      const response = await connectionsApi.update(connectionId, data);
      return response.data;
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not update connection."));
    }
  },
);

export const disableConnection = createAsyncThunk(
  "connection/disableConnection",
  async (connectionId, { dispatch, rejectWithValue }) => {
    try {
      if (!isValidId(connectionId)) return rejectWithValue("Invalid connection id.");
      const response = await connectionsApi.deactivate(connectionId);
      dispatch(fetchConnections());
      return response.data;
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not disable connection."));
    }
  },
);

export const deleteConnection = createAsyncThunk(
  "connection/deleteConnection",
  async (connectionId, { rejectWithValue }) => {
    try {
      if (!isValidId(connectionId)) return rejectWithValue("Invalid connection id.");
      await connectionsApi.delete(connectionId);
      return connectionId;
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not delete connection."));
    }
  },
);

export const testConnection = createAsyncThunk(
  "connection/testConnection",
  async (connectionId, { rejectWithValue }) => {
    try {
      if (!isValidId(connectionId)) return rejectWithValue("Invalid connection id.");
      const response = await connectionsApi.test(connectionId);
      return response.data;
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Connection test failed."));
    }
  },
);

export const fetchCatalogs = createAsyncThunk(
  "connection/fetchCatalogs",
  async (connectionId, { rejectWithValue }) => {
    try {
      if (!isValidId(connectionId)) return rejectWithValue("Invalid connection id.");
      const response = await connectionsApi.listCatalogs(connectionId);
      return response.data || [];
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not load catalogs."));
    }
  },
);

export const fetchSchemas = createAsyncThunk(
  "connection/fetchSchemas",
  async (connectionId, { rejectWithValue }) => {
    try {
      if (!isValidId(connectionId)) return rejectWithValue("Invalid connection id.");
      const response = await connectionsApi.listSchemas(connectionId);
      return response.data || [];
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not load schemas."));
    }
  },
);

export const fetchRemoteTables = createAsyncThunk(
  "connection/fetchRemoteTables",
  async ({ connectionId, schema }, { rejectWithValue }) => {
    try {
      if (!isValidId(connectionId)) return rejectWithValue("Invalid connection id.");
      const response = await connectionsApi.listTables(connectionId, schema);
      return response.data || [];
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not load tables."));
    }
  },
);

export const fetchManagedTables = createAsyncThunk(
  "connection/fetchManagedTables",
  async (connectionId, { rejectWithValue }) => {
    try {
      if (!isValidId(connectionId)) return rejectWithValue("Invalid connection id.");
      const response = await connectionsApi.listManagedTables(connectionId);
      return response.data || [];
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not load managed tables."));
    }
  },
);

export const addManagedTables = createAsyncThunk(
  "connection/addManagedTables",
  async ({ connectionId, catalog, schema, tableNames }, { dispatch, rejectWithValue }) => {
    try {
      if (!isValidId(connectionId)) return rejectWithValue("Invalid connection id.");
      const results = await Promise.allSettled(
        tableNames.map((tableName) => tablesApi.create({
          connection_id: connectionId,
          catalog_name: catalog,
          schema_name: schema,
          table_name: tableName,
        })),
      );
      await dispatch(fetchManagedTables(connectionId));
      return {
        added: results.filter((result) => result.status === "fulfilled").length,
        skipped: results.filter((result) => result.status === "rejected").length,
      };
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not add managed tables."));
    }
  },
);

export const disableManagedTable = createAsyncThunk(
  "connection/disableManagedTable",
  async ({ connectionId, tableId }, { dispatch, rejectWithValue }) => {
    try {
      if (!isValidId(connectionId)) return rejectWithValue("Invalid connection id.");
      const response = await tablesApi.deactivate(tableId);
      await dispatch(fetchManagedTables(connectionId));
      return response.data;
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not disable table."));
    }
  },
);

export const deleteManagedTable = createAsyncThunk(
  "connection/deleteManagedTable",
  async ({ connectionId, tableId }, { dispatch, rejectWithValue }) => {
    try {
      if (!isValidId(connectionId)) return rejectWithValue("Invalid connection id.");
      await tablesApi.delete(tableId);
      await dispatch(fetchManagedTables(connectionId));
      return tableId;
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not delete table."));
    }
  },
);

const initialState = {
  connections: [],
  currentConnection: null,
  managedTables: [],
  catalogs: [],
  schemas: [],
  remoteTables: [],
  listStatus: "idle",
  detailStatus: "idle",
  mutationStatus: "idle",
  testStatus: "idle",
  discoveryStatus: "idle",
  managedTablesStatus: "idle",
  error: null,
  testResult: null,
};

const connectionSlice = createSlice({
  name: "connection",
  initialState,
  reducers: {
    resetConnectionMutation(state) {
      state.mutationStatus = "idle";
      state.error = null;
    },
    resetConnectionTest(state) {
      state.testStatus = "idle";
      state.testResult = null;
    },
    clearConnectionDetail(state) {
      state.currentConnection = null;
      state.managedTables = [];
      state.catalogs = [];
      state.schemas = [];
      state.remoteTables = [];
      state.detailStatus = "idle";
      state.discoveryStatus = "idle";
      state.managedTablesStatus = "idle";
      state.error = null;
      state.testResult = null;
    },
    clearDiscovery(state) {
      state.remoteTables = [];
      state.discoveryStatus = "idle";
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchConnections.pending, (state) => {
        state.listStatus = "loading";
      })
      .addCase(fetchConnections.fulfilled, (state, action) => {
        state.listStatus = "succeeded";
        state.connections = action.payload;
      })
      .addCase(fetchConnections.rejected, (state, action) => {
        state.listStatus = "failed";
        state.error = action.payload;
      })
      .addCase(fetchConnection.pending, (state) => {
        state.detailStatus = "loading";
      })
      .addCase(fetchConnection.fulfilled, (state, action) => {
        state.detailStatus = "succeeded";
        state.currentConnection = action.payload;
      })
      .addCase(fetchConnection.rejected, (state, action) => {
        state.detailStatus = "failed";
        state.error = action.payload;
      })
      .addCase(createConnection.pending, (state) => {
        state.mutationStatus = "loading";
      })
      .addCase(createConnection.fulfilled, (state, action) => {
        state.mutationStatus = "succeeded";
        state.currentConnection = action.payload;
        state.connections.unshift(action.payload);
      })
      .addCase(updateConnection.pending, (state) => {
        state.mutationStatus = "loading";
      })
      .addCase(updateConnection.fulfilled, (state, action) => {
        state.mutationStatus = "succeeded";
        state.currentConnection = action.payload;
        state.connections = state.connections.map((connection) => (
          connection.id === action.payload.id ? action.payload : connection
        ));
      })
      .addCase(deleteConnection.fulfilled, (state, action) => {
        state.connections = state.connections.filter((connection) => connection.id !== action.payload);
      })
      .addCase(disableConnection.fulfilled, (state, action) => {
        state.connections = state.connections.map((connection) => (
          connection.id === action.payload.id ? action.payload : connection
        ));
      })
      .addCase(testConnection.pending, (state) => {
        state.testStatus = "loading";
        state.testResult = null;
      })
      .addCase(testConnection.fulfilled, (state, action) => {
        state.testStatus = "succeeded";
        state.testResult = action.payload;
      })
      .addCase(testConnection.rejected, (state, action) => {
        state.testStatus = "failed";
        state.error = action.payload;
      })
      .addCase(fetchCatalogs.pending, (state) => {
        state.discoveryStatus = "loading";
      })
      .addCase(fetchCatalogs.fulfilled, (state, action) => {
        state.discoveryStatus = "succeeded";
        state.catalogs = action.payload;
      })
      .addCase(fetchSchemas.pending, (state) => {
        state.discoveryStatus = "loading";
        state.schemas = [];
        state.remoteTables = [];
      })
      .addCase(fetchSchemas.fulfilled, (state, action) => {
        state.discoveryStatus = "succeeded";
        state.schemas = action.payload;
      })
      .addCase(fetchRemoteTables.pending, (state) => {
        state.discoveryStatus = "loading";
        state.remoteTables = [];
      })
      .addCase(fetchRemoteTables.fulfilled, (state, action) => {
        state.discoveryStatus = "succeeded";
        state.remoteTables = action.payload;
      })
      .addCase(fetchManagedTables.pending, (state) => {
        state.managedTablesStatus = "loading";
      })
      .addCase(fetchManagedTables.fulfilled, (state, action) => {
        state.managedTablesStatus = "succeeded";
        state.managedTables = action.payload;
      })
      .addMatcher(
        (action) => action.type.startsWith("connection/") && action.type.endsWith("/rejected"),
        (state, action) => {
          state.error = action.payload || action.error?.message || null;
          if (state.mutationStatus === "loading") state.mutationStatus = "failed";
          if (state.discoveryStatus === "loading") state.discoveryStatus = "failed";
          if (state.managedTablesStatus === "loading") state.managedTablesStatus = "failed";
        },
      )
      .addMatcher(
        (action) => (
          [
            disableManagedTable.fulfilled.type,
            deleteManagedTable.fulfilled.type,
            addManagedTables.fulfilled.type,
          ].includes(action.type)
        ),
        (state) => {
          state.mutationStatus = "succeeded";
        },
      );
  },
});

export const {
  clearConnectionDetail,
  clearDiscovery,
  resetConnectionMutation,
  resetConnectionTest,
} = connectionSlice.actions;

export default connectionSlice.reducer;
