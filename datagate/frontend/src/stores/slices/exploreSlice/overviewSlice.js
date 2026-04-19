import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { exploreApi } from "~/apis/explore";
import { getErrorMessage } from "~/utils/errorUtils";

export const fetchAssetOverview = createAsyncThunk(
  "overview/fetchAssetOverview",
  async ({ tableName, schemaName, serviceId }, { rejectWithValue }) => {
    try {
      const response = await exploreApi.getAssetOverview({
        table: tableName,
        schema: schemaName || null,
        service_id: serviceId,
      });
      return { key: `${serviceId}:${schemaName || 'public'}:${tableName}`, data: response.data };
    } catch (error) {
      return rejectWithValue({
        key: `${serviceId}:${schemaName || 'public'}:${tableName}`,
        message: getErrorMessage(error, "Could not load asset overview."),
      });
    }
  }
);

export const fetchAssetSample = createAsyncThunk(
  "overview/fetchAssetSample",
  async ({ tableName, schemaName, serviceId, sampleLimit = 50 }, { rejectWithValue }) => {
    try {
      const response = await exploreApi.getAssetSample({
        table: tableName,
        schema: schemaName || null,
        service_id: serviceId,
        sample_limit: sampleLimit,
      });
      const key = `${serviceId}:${schemaName || 'public'}:${tableName}:${sampleLimit}`;
      return { key, data: response.data };
    } catch (error) {
      const key = `${serviceId}:${schemaName || 'public'}:${tableName}:${sampleLimit}`;
      return rejectWithValue({
        key,
        message: getErrorMessage(error, "Could not load asset sample."),
      });
    }
  }
);

const initialState = {
  assetOverviewsByKey: {},
  assetOverviewStatusByKey: {},
  assetOverviewErrorByKey: {},
  assetSamplesByKey: {},
  assetSampleStatusByKey: {},
};

const overviewSlice = createSlice({
  name: "overview",
  initialState,
  reducers: {
    clearOverviewCache: (state) => {
      state.assetOverviewsByKey = {};
      state.assetSamplesByKey = {};
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAssetOverview.pending, (state, action) => {
        const { tableName, serviceId, schemaName } = action.meta.arg;
        const key = `${serviceId}:${schemaName || 'public'}:${tableName}`;
        state.assetOverviewStatusByKey[key] = "loading";
      })
      .addCase(fetchAssetOverview.fulfilled, (state, action) => {
        const { key, data } = action.payload;
        state.assetOverviewStatusByKey[key] = "succeeded";
        state.assetOverviewsByKey[key] = data;
      })
      .addCase(fetchAssetOverview.rejected, (state, action) => {
        const { key, message } = action.payload || {};
        if (key) {
          state.assetOverviewStatusByKey[key] = "failed";
          state.assetOverviewErrorByKey[key] = message;
        }
      })
      .addCase(fetchAssetSample.pending, (state, action) => {
        const { tableName, serviceId, schemaName, sampleLimit = 50 } = action.meta.arg;
        const key = `${serviceId}:${schemaName || 'public'}:${tableName}:${sampleLimit}`;
        state.assetSampleStatusByKey[key] = "loading";
      })
      .addCase(fetchAssetSample.fulfilled, (state, action) => {
        const { key, data } = action.payload;
        state.assetSampleStatusByKey[key] = "succeeded";
        state.assetSamplesByKey[key] = data;
      });
  },
});

export const { clearOverviewCache } = overviewSlice.actions;
export default overviewSlice.reducer;
