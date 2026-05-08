import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { usersApi } from "~/apis/api";

export const fetchUsers = createAsyncThunk("user/list", async (params, { rejectWithValue }) => {
  try {
    const res = await usersApi.list(params);
    return res.data;
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const fetchUser = createAsyncThunk("user/get", async (id, { rejectWithValue }) => {
  try {
    const res = await usersApi.get(id);
    return res.data;
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const createUser = createAsyncThunk("user/create", async (data, { rejectWithValue }) => {
  try {
    const res = await usersApi.create(data);
    return res.data;
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const updateUser = createAsyncThunk("user/update", async ({ id, data }, { rejectWithValue }) => {
  try {
    const res = await usersApi.update(id, data);
    return res.data;
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const activateUser = createAsyncThunk("user/activate", async (id, { rejectWithValue }) => {
  try {
    const res = await usersApi.activate(id);
    return res.data;
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const deactivateUser = createAsyncThunk("user/deactivate", async (id, { rejectWithValue }) => {
  try {
    const res = await usersApi.deactivate(id);
    return res.data;
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const assignUserRoles = createAsyncThunk("user/assignRoles", async ({ id, roleIds }, { rejectWithValue }) => {
  try {
    const res = await usersApi.assignRoles(id, { role_ids: roleIds });
    return res.data;
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const fetchMe = createAsyncThunk("user/fetchMe", async (_, { rejectWithValue }) => {
  try {
    const res = await usersApi.getMe();
    return res.data;
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const updateMe = createAsyncThunk("user/updateMe", async (data, { rejectWithValue }) => {
  try {
    const res = await usersApi.updateMe(data);
    return res.data;
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

const initialState = {
  users: [],
  currentUser: null,
  total: 0,
  page: 1,
  pageSize: 20,
  loading: false,
  error: null,
};

const userSlice = createSlice({
  name: "user",
  initialState,
  reducers: {
    clearError: (state) => { state.error = null; },
    clearCurrentUser: (state) => { state.currentUser = null; }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.users = action.payload.items;
        state.total = action.payload.total;
        state.page = action.payload.page;
        state.pageSize = action.payload.page_size;
      })
      .addCase(fetchUser.fulfilled, (state, action) => { state.currentUser = action.payload; })
      .addCase(createUser.fulfilled, (state, action) => { state.users.unshift(action.payload); })
      .addCase(updateUser.fulfilled, (state, action) => {
        if (state.currentUser?.id === action.payload.id) state.currentUser = action.payload;
        state.users = state.users.map(u => u.id === action.payload.id ? action.payload : u);
      })
      .addCase(activateUser.fulfilled, (state, action) => {
        if (state.currentUser?.id === action.payload.id) state.currentUser = action.payload;
        state.users = state.users.map(u => u.id === action.payload.id ? action.payload : u);
      })
      .addCase(deactivateUser.fulfilled, (state, action) => {
        if (state.currentUser?.id === action.payload.id) state.currentUser = action.payload;
        state.users = state.users.map(u => u.id === action.payload.id ? action.payload : u);
      })
      .addCase(assignUserRoles.fulfilled, (state, action) => {
        if (state.currentUser?.id === action.payload.id) state.currentUser = action.payload;
        state.users = state.users.map(u => u.id === action.payload.id ? action.payload : u);
      })
      .addCase(fetchMe.fulfilled, (state, action) => { state.currentUser = action.payload; })
      .addCase(updateMe.fulfilled, (state, action) => { state.currentUser = action.payload; })
      .addMatcher(action => action.type.endsWith("/pending"), (state) => { state.loading = true; state.error = null; })
      .addMatcher(action => action.type.endsWith("/fulfilled"), (state) => { state.loading = false; })
      .addMatcher(action => action.type.endsWith("/rejected"), (state, action) => { state.loading = false; state.error = action.payload; });
  },
});

export const { clearError, clearCurrentUser } = userSlice.actions;
export default userSlice.reducer;
