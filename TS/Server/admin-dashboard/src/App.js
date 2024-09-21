// src/App.js

import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./App.css";
import AdminDashboard from "./components/AdminDashBoard/AdminDashboard";
import GameTester from "./components/GameTester/GameTester"; // New import

function App() {
  return (
    <Router>
      <div>
        <nav>
          <ul>
            <li>
              <Link to="/">Admin Dashboard</Link>
            </li>
            <li>
              <Link to="/game-tester">Game Tester</Link>
            </li>
          </ul>
        </nav>
        <Routes>
          <Route path="/" element={<AdminDashboard />} />
          <Route path="/game-tester" element={<GameTester />} />
        </Routes>
        <ToastContainer />
      </div>
    </Router>
  );
}

export default App;
