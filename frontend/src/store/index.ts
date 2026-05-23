import { configureStore } from '@reduxjs/toolkit'
import { combineReducers } from 'redux'

import weatherReducer from './slices/weatherSlice'
import alertsReducer from './slices/alertsSlice'
import userReducer from './slices/userSlice'
import uiReducer from './slices/uiSlice'

export const rootReducer = combineReducers({
  weather: weatherReducer,
  alerts: alertsReducer,
  user: userReducer,
  ui: uiReducer,
})

export type RootState = ReturnType<typeof rootReducer>

const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore non-serializable data from third-party libraries
        ignoredActions: ['persist/PERSIST'],
        ignoredPaths: ['_persist'],
      },
    }),
  devTools: import.meta.env.DEV,
})

export type AppDispatch = typeof store.dispatch

export default store
