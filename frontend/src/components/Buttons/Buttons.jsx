import React from "react";
import "./Buttons.css";
import { useNavigate } from "react-router-dom";
const Buttons = () => {
  const navigate = useNavigate();
  return (
    <button className="get-started-btn" onClick={()=>{navigate("/auth")}}>
      Get Started
    </button>
  );
};

export default Buttons;