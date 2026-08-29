import React from "react";
import white_logo from "../../assets/logo_logs_tree_white.png";
import Buttons from "../Buttons/Buttons";
import "./TopBar.css";

const TopBar = () => {
  return (
    <div className="topbar">
      <div className="logo-section">
        <span>Logs</span>
      </div>
      <Buttons />
    </div>
  );
};

export default TopBar;
