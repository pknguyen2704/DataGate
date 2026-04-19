import { combineReducers } from "@reduxjs/toolkit";
import discoveryReducer from "./discoverySlice";
import overviewReducer from "./overviewSlice";
import observabilityReducer from "./observabilitySlice";

const exploreReducer = combineReducers({
  discovery: discoveryReducer,
  overview: overviewReducer,
  observability: observabilityReducer,
});

export default exploreReducer;

export * from "./discoverySlice";
export * from "./overviewSlice";
export * from "./observabilitySlice";
