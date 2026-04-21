import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { exploreApi } from "~/apis/explore";
import { connectionsApi } from "~/apis/connections";
import { getErrorMessage } from "~/utils/errorUtils";

export const fetchConnections = createAsyncThunk(
  "discovery/fetchConnections",
  async (_, { rejectWithValue }) => {
    try {
      const response = await connectionsApi.getConnections();
      return response.data || [];
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not load connections."));
    }
  }
);

export const fetchExploreData = createAsyncThunk(
  "discovery/fetchExploreData",
  async (_, { rejectWithValue }) => {
    try {
      const response = await exploreApi.getExploreData();
      return response.data || [];
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not load explore data."));
    }
  }
);

const initialState = {
  connections: [],
  connectionsStatus: "idle",
  connectionsError: null,
  exploreDataLoaded: false,
  schemasByConnection: {},
  tablesByConnection: {},
};

const discoverySlice = createSlice({
  name: "discovery",
  initialState,
  reducers: {
    clearDiscoveryCache: (state) => {
      state.connections = [];
      state.exploreDataLoaded = false;
      state.schemasByConnection = {};
      state.tablesByConnection = {};
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchConnections.pending, (state) => {
        state.connectionsStatus = "loading";
      })
      .addCase(fetchConnections.fulfilled, (state, action) => {
        state.connectionsStatus = "succeeded";
        state.connections = action.payload;
      })
      .addCase(fetchConnections.rejected, (state, action) => {
        state.connectionsStatus = "failed";
        state.connectionsError = action.payload;
      })
      .addCase(fetchExploreData.pending, (state) => {
        state.connectionsStatus = "loading";
      })
      .addCase(fetchExploreData.fulfilled, (state, action) => {
        state.connectionsStatus = "succeeded";
        state.exploreDataLoaded = true;
        const exploreData = action.payload;
        state.connections = exploreData.map(d => d.connection);
        exploreData.forEach(d => {
          state.schemasByConnection[d.connection.id] = d.schemas;
          state.tablesByConnection[d.connection.id] = d.tables;
        });
      })
      .addCase(fetchExploreData.rejected, (state, action) => {
        state.connectionsStatus = "failed";
        state.connectionsError = action.payload;
      });
  },
});

export const { clearDiscoveryCache } = discoverySlice.actions;
export default discoverySlice.reducer;
