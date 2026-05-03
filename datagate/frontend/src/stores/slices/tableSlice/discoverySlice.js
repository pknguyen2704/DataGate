import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { exploreApi } from "~/apis/exploreApi";
import { getErrorMessage } from "~/utils/errorUtils";

const buildCatalogMap = (catalogs) =>
  catalogs.reduce((acc, catalog) => {
    acc[catalog.catalog_name] = catalog;
    return acc;
  }, {});

const buildSchemaMap = (catalogs) =>
  catalogs.reduce((acc, catalog) => {
    acc[catalog.catalog_name] = (catalog.schemas || []).reduce((schemaAcc, schema) => {
      schemaAcc[schema.schema_name] = schema;
      return schemaAcc;
    }, {});
    return acc;
  }, {});

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
  catalogs: [],
  catalogMap: {},
  schemaMapByCatalog: {},
  discoveryStatus: "idle",
  discoveryError: null,
  exploreDataLoaded: false,
};

const discoverySlice = createSlice({
  name: "discovery",
  initialState,
  reducers: {
    clearDiscoveryCache: (state) => {
      state.catalogs = [];
      state.catalogMap = {};
      state.schemaMapByCatalog = {};
      state.discoveryStatus = "idle";
      state.discoveryError = null;
      state.exploreDataLoaded = false;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchExploreData.pending, (state) => {
        state.discoveryStatus = "loading";
        state.discoveryError = null;
      })
      .addCase(fetchExploreData.fulfilled, (state, action) => {
        const catalogs = action.payload;
        state.discoveryStatus = "succeeded";
        state.discoveryError = null;
        state.exploreDataLoaded = true;
        state.catalogs = catalogs;
        state.catalogMap = buildCatalogMap(catalogs);
        state.schemaMapByCatalog = buildSchemaMap(catalogs);
      })
      .addCase(fetchExploreData.rejected, (state, action) => {
        state.discoveryStatus = "failed";
        state.discoveryError = action.payload;
      });
  },
});

export const { clearDiscoveryCache } = discoverySlice.actions;
export default discoverySlice.reducer;
