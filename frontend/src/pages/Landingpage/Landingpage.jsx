import React from "react";
import Hero from "./Hero/Hero";
import TopBar from "../../components/TopBar/TopBar";
import "./Landingpage.css";
const Landingpage = () => {
  return (
    <div className="landing-page">
      <TopBar />
      <Hero />
    </div>
  );
};

export default Landingpage;
