import React from "react";
import white_logo from "../../assets/logo_logs_tree_white.png";
import Buttons from "../Buttons/Buttons";
import "./TopBar.css";

const TopBar = () => {
  return (
    <div className="topbar">
      <div className="logo-section">
        <img src={white_logo} id="white_logo" alt="Logs logo" />
        <span>Logs</span>
      </div>

      <Buttons />
    </div>
  );
};

export default TopBar;
