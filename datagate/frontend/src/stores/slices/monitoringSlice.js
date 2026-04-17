import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { profilingApi } from "~/apis/profiling";

const getErrorMessage = (error, fallback) =>
  error.response?.data?.detail || error.message || fallback;

export const fetchMonitoringRecommendations = createAsyncThunk(
  "monitoring/fetchRecommendations",
  async (tableName, { rejectWithValue }) => {
    try {
      const response = await profilingApi.getMonitoringRecommendations(tableName);
      return {
        tableName,
        recommendations: response.data?.recommended_columns || [],
      };
    } catch (error) {
      return rejectWithValue({
        tableName,
        message: getErrorMessage(error, "No profiling recommendations are available for this asset yet."),
      });
    }
  }
);

export const fetchMonitoringSeries = createAsyncThunk(
  "monitoring/fetchSeries",
  async ({ tableName, columnName, metric, confidence }, { rejectWithValue }) => {
    try {
      const response = await profilingApi.getMonitoringSeries(
        tableName,
        columnName,
        metric,
        confidence
      );
      return {
        key: `${tableName}:${columnName}:${metric}:${confidence}`,
        points: response.data?.points || [],
      };
    } catch (error) {
      return rejectWithValue({
        key: `${tableName}:${columnName}:${metric}:${confidence}`,
        message: getErrorMessage(error, "Could not load metric history for the selected column."),
      });
    }
  }
);

const initialState = {
  recommendationsByTable: {},
  recommendationsStatusByTable: {},
  recommendationsErrorByTable: {},
  seriesByKey: {},
  seriesStatusByKey: {},
  seriesErrorByKey: {},
};

const monitoringSlice = createSlice({
  name: "monitoring",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchMonitoringRecommendations.pending, (state, action) => {
        const tableName = action.meta.arg;
        state.recommendationsStatusByTable[tableName] = "loading";
        state.recommendationsErrorByTable[tableName] = null;
      })
      .addCase(fetchMonitoringRecommendations.fulfilled, (state, action) => {
        const { tableName, recommendations } = action.payload;
        state.recommendationsStatusByTable[tableName] = "succeeded";
        state.recommendationsByTable[tableName] = recommendations;
      })
      .addCase(fetchMonitoringRecommendations.rejected, (state, action) => {
        const { tableName, message } = action.payload || {};
        if (tableName) {
          state.recommendationsStatusByTable[tableName] = "failed";
          state.recommendationsErrorByTable[tableName] = message;
        }
      })
      .addCase(fetchMonitoringSeries.pending, (state, action) => {
        const { tableName, columnName, metric, confidence } = action.meta.arg;
        const key = `${tableName}:${columnName}:${metric}:${confidence}`;
        state.seriesStatusByKey[key] = "loading";
        state.seriesErrorByKey[key] = null;
      })
      .addCase(fetchMonitoringSeries.fulfilled, (state, action) => {
        const { key, points } = action.payload;
        state.seriesStatusByKey[key] = "succeeded";
        state.seriesByKey[key] = points;
      })
      .addCase(fetchMonitoringSeries.rejected, (state, action) => {
        const { key, message } = action.payload || {};
        if (key) {
          state.seriesStatusByKey[key] = "failed";
          state.seriesErrorByKey[key] = message;
        }
      });
  },
});

export default monitoringSlice.reducer;
