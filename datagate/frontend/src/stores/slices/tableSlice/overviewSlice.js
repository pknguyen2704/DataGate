import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { exploreApi } from "~/apis/exploreApi";
import { getErrorMessage } from "~/utils/errorUtils";

const buildAssetKey = ({ tableName, schemaName, catalogName }) =>
  `${catalogName || "default"}:${schemaName || "public"}:${tableName}`;

const buildSampleKey = ({ tableName, schemaName, catalogName, sampleLimit = 50 }) =>
  `${buildAssetKey({ tableName, schemaName, catalogName })}:${sampleLimit}`;

export const fetchAssetOverview = createAsyncThunk(
  "overview/fetchAssetOverview",
  async ({ tableName, schemaName, catalogName }, { rejectWithValue }) => {
    const key = buildAssetKey({ tableName, schemaName, catalogName });
    try {
      const response = await exploreApi.getAssetOverview({
        table: tableName,
        schema: schemaName,
        catalog: catalogName,
      });
      return { key, data: response.data };
    } catch (error) {
      return rejectWithValue({
        key,
        message: getErrorMessage(error, "Could not load asset overview."),
      });
    }
  }
);

export const fetchAssetSample = createAsyncThunk(
  "overview/fetchAssetSample",
  async ({ tableName, schemaName, catalogName, sampleLimit = 50 }, { rejectWithValue }) => {
    const key = buildSampleKey({ tableName, schemaName, catalogName, sampleLimit });
    try {
      const response = await exploreApi.getAssetSample({
        table: tableName,
        schema: schemaName,
        catalog: catalogName,
        sampleLimit,
      });
      return { key, data: response.data };
    } catch (error) {
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
  assetSampleErrorByKey: {},
};

const overviewSlice = createSlice({
  name: "overview",
  initialState,
  reducers: {
    clearOverviewCache: (state) => {
      state.assetOverviewsByKey = {};
      state.assetOverviewStatusByKey = {};
      state.assetOverviewErrorByKey = {};
      state.assetSamplesByKey = {};
      state.assetSampleStatusByKey = {};
      state.assetSampleErrorByKey = {};
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAssetOverview.pending, (state, action) => {
        const key = buildAssetKey(action.meta.arg);
        state.assetOverviewStatusByKey[key] = "loading";
        state.assetOverviewErrorByKey[key] = null;
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
        const key = buildSampleKey(action.meta.arg);
        state.assetSampleStatusByKey[key] = "loading";
        state.assetSampleErrorByKey[key] = null;
      })
      .addCase(fetchAssetSample.fulfilled, (state, action) => {
        const { key, data } = action.payload;
        state.assetSampleStatusByKey[key] = "succeeded";
        state.assetSamplesByKey[key] = data;
      })
      .addCase(fetchAssetSample.rejected, (state, action) => {
        const { key, message } = action.payload || {};
        if (key) {
          state.assetSampleStatusByKey[key] = "failed";
          state.assetSampleErrorByKey[key] = message;
        }
      });
  },
});

export const { clearOverviewCache } = overviewSlice.actions;
export default overviewSlice.reducer;
