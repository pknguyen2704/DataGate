import api from "./api";
export const exploreApi = {
  getExploreData: () => api.get('/explore'),
};
