import React from "react";
import black_logo from "../../../assets/black_logo_logs.png";
import "./Hero.css";

const Hero = () => {
  return (
    <div className="hero">
      <div className="main-text">
        I build cool sh*t <br />❝ <span className="title-text">LOGS</span>
        <span>
          <img src={black_logo} className="logo-hero" />
        </span>
        remembers what I did .<br />
        Then I post it ❞
      </div>
    </div>
  );
};

export default Hero;
