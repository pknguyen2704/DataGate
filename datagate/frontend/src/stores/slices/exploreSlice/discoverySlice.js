import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { exploreApi } from "~/apis/explore";
import { servicesApi } from "~/apis/services";
import { getErrorMessage } from "~/utils/errorUtils";

export const fetchServices = createAsyncThunk(
  "discovery/fetchServices",
  async (_, { rejectWithValue }) => {
    try {
      const response = await servicesApi.getServices();
      return response.data || [];
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not load services."));
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

export const fetchServiceSchemas = createAsyncThunk(
  "discovery/fetchServiceSchemas",
  async (serviceId, { rejectWithValue }) => {
    try {
      const response = await servicesApi.getServiceSchemas(serviceId);
      return { serviceId, schemas: response.data || [] };
    } catch (error) {
      return rejectWithValue({
        serviceId,
        message: getErrorMessage(error, "Could not load schemas."),
      });
    }
  }
);

export const fetchServiceTables = createAsyncThunk(
  "discovery/fetchServiceTables",
  async (serviceId, { rejectWithValue }) => {
    try {
      const response = await servicesApi.getServiceTables(serviceId);
      return { serviceId, tables: response.data || [] };
    } catch (error) {
      return rejectWithValue({
        serviceId,
        message: getErrorMessage(error, "Could not load tables."),
      });
    }
  }
);

const initialState = {
  services: [],
  servicesStatus: "idle",
  servicesError: null,
  exploreDataLoaded: false,
  schemasByService: {},
  tablesByService: {},
  tablesStatusByService: {},
};

const discoverySlice = createSlice({
  name: "discovery",
  initialState,
  reducers: {
    clearDiscoveryCache: (state) => {
      state.services = [];
      state.exploreDataLoaded = false;
      state.schemasByService = {};
      state.tablesByService = {};
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchServices.pending, (state) => {
        state.servicesStatus = "loading";
        state.servicesError = null;
      })
      .addCase(fetchServices.fulfilled, (state, action) => {
        state.servicesStatus = "succeeded";
        state.services = action.payload;
      })
      .addCase(fetchServices.rejected, (state, action) => {
        state.servicesStatus = "failed";
        state.servicesError = action.payload;
      })
      .addCase(fetchExploreData.pending, (state) => {
        state.servicesStatus = "loading";
        state.servicesError = null;
      })
      .addCase(fetchExploreData.fulfilled, (state, action) => {
        state.servicesStatus = "succeeded";
        state.exploreDataLoaded = true;
        const exploreData = action.payload;
        state.services = exploreData.map(d => d.service);
        exploreData.forEach(d => {
          state.schemasByService[d.service.id] = d.schemas;
          state.tablesByService[d.service.id] = d.tables;
          state.tablesStatusByService[d.service.id] = "succeeded";
        });
      })
      .addCase(fetchExploreData.rejected, (state, action) => {
        state.servicesStatus = "failed";
        state.servicesError = action.payload;
      })
      .addCase(fetchServiceSchemas.fulfilled, (state, action) => {
        const { serviceId, schemas } = action.payload;
        state.schemasByService[serviceId] = schemas;
      })
      .addCase(fetchServiceTables.pending, (state, action) => {
        const serviceId = action.meta.arg;
        state.tablesStatusByService[serviceId] = "loading";
      })
      .addCase(fetchServiceTables.fulfilled, (state, action) => {
        const { serviceId, tables } = action.payload;
        state.tablesStatusByService[serviceId] = "succeeded";
        state.tablesByService[serviceId] = tables;
      })
      .addCase(fetchServiceTables.rejected, (state, action) => {
        const { serviceId } = action.payload || {};
        if (serviceId) {
          state.tablesStatusByService[serviceId] = "failed";
        }
      });
  },
});

export const { clearDiscoveryCache } = discoverySlice.actions;
export default discoverySlice.reducer;
