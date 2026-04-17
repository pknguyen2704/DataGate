import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { servicesApi } from "~/apis/services";

const getErrorMessage = (error, fallback) =>
  error.response?.data?.detail || error.message || fallback;

export const fetchServices = createAsyncThunk(
  "services/fetchServices",
  async (_, { rejectWithValue }) => {
    try {
      const response = await servicesApi.getServices();
      return response.data || [];
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not load services."));
    }
  }
);

export const fetchAssets = createAsyncThunk(
  "services/fetchAssets",
  async (_, { rejectWithValue }) => {
    try {
      const response = await servicesApi.getAssets();
      return response.data || [];
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not load assets."));
    }
  }
);

export const fetchServiceSchemas = createAsyncThunk(
  "services/fetchServiceSchemas",
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
  "services/fetchServiceTables",
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

export const fetchAssetDetail = createAsyncThunk(
  "services/fetchAssetDetail",
  async ({ tableName, serviceId, sampleLimit = 50 }, { rejectWithValue }) => {
    try {
      const response = await servicesApi.getAssetDetail(tableName, serviceId, sampleLimit);
      return {
        key: `${serviceId}:${tableName}:${sampleLimit}`,
        tableName,
        serviceId,
        sampleLimit,
        data: response.data,
      };
    } catch (error) {
      return rejectWithValue({
        key: `${serviceId}:${tableName}:${sampleLimit}`,
        message: getErrorMessage(error, "Could not load asset details."),
      });
    }
  }
);

export const createService = createAsyncThunk(
  "services/createService",
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
  "services/updateService",
  async ({ serviceId, data }, { rejectWithValue }) => {
    try {
      const response = await servicesApi.updateService(serviceId, data);
      return response.data;
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not update service."));
    }
  }
);

export const refreshServiceTables = createAsyncThunk(
  "services/refreshServiceTables",
  async (serviceId, { rejectWithValue }) => {
    try {
      await servicesApi.refreshTables(serviceId);
      return serviceId;
    } catch (error) {
      return rejectWithValue({
        serviceId,
        message: getErrorMessage(error, "Could not refresh service tables."),
      });
    }
  }
);

export const deleteService = createAsyncThunk(
  "services/deleteService",
  async (serviceId, { rejectWithValue }) => {
    try {
      await servicesApi.deleteService(serviceId);
      return serviceId;
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, "Could not delete service."));
    }
  }
);

const initialState = {
  services: [],
  servicesStatus: "idle",
  servicesError: null,
  assets: [],
  assetsStatus: "idle",
  assetsError: null,
  schemasByService: {},
  schemasStatusByService: {},
  schemasErrorByService: {},
  tablesByService: {},
  tablesStatusByService: {},
  tablesErrorByService: {},
  assetDetailsByKey: {},
  assetDetailStatusByKey: {},
  assetDetailErrorByKey: {},
  mutationStatus: "idle",
  mutationError: null,
  refreshingByService: {},
};

const servicesSlice = createSlice({
  name: "services",
  initialState,
  reducers: {},
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
      .addCase(fetchAssets.pending, (state) => {
        state.assetsStatus = "loading";
        state.assetsError = null;
      })
      .addCase(fetchAssets.fulfilled, (state, action) => {
        state.assetsStatus = "succeeded";
        state.assets = action.payload;
      })
      .addCase(fetchAssets.rejected, (state, action) => {
        state.assetsStatus = "failed";
        state.assetsError = action.payload;
      })
      .addCase(fetchServiceSchemas.pending, (state, action) => {
        const serviceId = action.meta.arg;
        state.schemasStatusByService[serviceId] = "loading";
        state.schemasErrorByService[serviceId] = null;
      })
      .addCase(fetchServiceSchemas.fulfilled, (state, action) => {
        const { serviceId, schemas } = action.payload;
        state.schemasStatusByService[serviceId] = "succeeded";
        state.schemasByService[serviceId] = schemas;
      })
      .addCase(fetchServiceSchemas.rejected, (state, action) => {
        const { serviceId, message } = action.payload || {};
        if (serviceId) {
          state.schemasStatusByService[serviceId] = "failed";
          state.schemasErrorByService[serviceId] = message;
        }
      })
      .addCase(fetchServiceTables.pending, (state, action) => {
        const serviceId = action.meta.arg;
        state.tablesStatusByService[serviceId] = "loading";
        state.tablesErrorByService[serviceId] = null;
      })
      .addCase(fetchServiceTables.fulfilled, (state, action) => {
        const { serviceId, tables } = action.payload;
        state.tablesStatusByService[serviceId] = "succeeded";
        state.tablesByService[serviceId] = tables;
      })
      .addCase(fetchServiceTables.rejected, (state, action) => {
        const { serviceId, message } = action.payload || {};
        if (serviceId) {
          state.tablesStatusByService[serviceId] = "failed";
          state.tablesErrorByService[serviceId] = message;
        }
      })
      .addCase(fetchAssetDetail.pending, (state, action) => {
        const { tableName, serviceId, sampleLimit = 50 } = action.meta.arg;
        const key = `${serviceId}:${tableName}:${sampleLimit}`;
        state.assetDetailStatusByKey[key] = "loading";
        state.assetDetailErrorByKey[key] = null;
      })
      .addCase(fetchAssetDetail.fulfilled, (state, action) => {
        const { key, data } = action.payload;
        state.assetDetailStatusByKey[key] = "succeeded";
        state.assetDetailsByKey[key] = data;
      })
      .addCase(fetchAssetDetail.rejected, (state, action) => {
        const { key, message } = action.payload || {};
        if (key) {
          state.assetDetailStatusByKey[key] = "failed";
          state.assetDetailErrorByKey[key] = message;
        }
      })
      .addCase(createService.pending, (state) => {
        state.mutationStatus = "loading";
        state.mutationError = null;
      })
      .addCase(createService.fulfilled, (state) => {
        state.mutationStatus = "succeeded";
      })
      .addCase(createService.rejected, (state, action) => {
        state.mutationStatus = "failed";
        state.mutationError = action.payload;
      })
      .addCase(updateService.pending, (state) => {
        state.mutationStatus = "loading";
        state.mutationError = null;
      })
      .addCase(updateService.fulfilled, (state) => {
        state.mutationStatus = "succeeded";
      })
      .addCase(updateService.rejected, (state, action) => {
        state.mutationStatus = "failed";
        state.mutationError = action.payload;
      })
      .addCase(refreshServiceTables.pending, (state, action) => {
        const serviceId = action.meta.arg;
        state.refreshingByService[serviceId] = true;
      })
      .addCase(refreshServiceTables.fulfilled, (state, action) => {
        state.refreshingByService[action.payload] = false;
      })
      .addCase(refreshServiceTables.rejected, (state, action) => {
        const serviceId = action.payload?.serviceId || action.meta.arg;
        state.refreshingByService[serviceId] = false;
      })
      .addCase(deleteService.pending, (state) => {
        state.mutationStatus = "loading";
        state.mutationError = null;
      })
      .addCase(deleteService.fulfilled, (state) => {
        state.mutationStatus = "succeeded";
      })
      .addCase(deleteService.rejected, (state, action) => {
        state.mutationStatus = "failed";
        state.mutationError = action.payload;
      });
  },
});

export default servicesSlice.reducer;
