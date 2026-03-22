import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Profiling from '~/pages/Profiling/Profiling';

function App() {
  return (
    <Routes>
      <Route path="/" element={
        <Navigate to="/home" replace={true} />
      }/>
      <Route path="/home" element={<h1>Đây là trang chủ nhưng mà lười nên chưa làm</h1>}/>
      <Route path="/profiling" element={<Profiling/>}/>
      <Route path='*' element={<h1>404 Not Found</h1>}/>
    </Routes>
  );
}

export default App;
