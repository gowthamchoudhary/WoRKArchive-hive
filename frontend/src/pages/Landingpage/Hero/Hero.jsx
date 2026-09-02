import React from "react";
import black_logo from "../../../assets/black_logo_logs.png";
import TextType from "./TextType";
import "./Hero.css";

const Hero = () => {
  return (
    <div className="hero">
      <div className="main-text">
        <TextType
          text={[
            "I build cool sh*t",
            "I design sleek interfaces",
            "I ship products fast",
          ]}
          typingSpeed={60}
          deletingSpeed={35}
          pauseDuration={1800}
          showCursor={true}
          cursorCharacter="|"
        />
        <br />❝ <span className="title-text">LOGS</span>
        <span>
          <img src={black_logo} className="logo-hero" alt="Logs logo" />
        </span>
        remembers what I did .<br />
        Then I post it ❞
      </div>
    </div>
  );
};

export default Hero;
