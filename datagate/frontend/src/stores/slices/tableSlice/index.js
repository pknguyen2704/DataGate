import { combineReducers } from "@reduxjs/toolkit";
import discoveryReducer from "./discoverySlice";
import overviewReducer from "./overviewSlice";

const exploreReducer = combineReducers({
  discovery: discoveryReducer,
  overview: overviewReducer,
});

export default exploreReducer;

export * from "./discoverySlice";
export * from "./overviewSlice";
