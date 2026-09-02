import React, { useState } from "react";
import { Eye, EyeOff } from "lucide-react";

import black_logo from "../../assets/black_logo_logs.png";
import "./Auth.css";

const Auth = () => {
  // true = Login
  // false = Signup
  const [login, setLogin] = useState(true);

  // Form states
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // Password visibility
  const [showPassword, setShowPassword] = useState(false);

  // Login / Signup
  async function authentication(e) {
    e.preventDefault();

    if (login) {
      // Login
      console.log("Login:", {
        email,
        password,
      });

      // Later:
      // const response = await loginUser(email, password);
      // navigate("/dashboard");
    } else {
      // Signup
      console.log("Signup:", {
        username,
        email,
        password,
      });

      // Later:
      // const response = await signupUser(username, email, password);
      // navigate("/dashboard");
    }
  }

  // Switch between Login and Signup
  function toggleAuth() {
    setLogin((prev) => !prev);

    // Clear form
    setUsername("");
    setEmail("");
    setPassword("");

    // Reset password visibility
    setShowPassword(false);
  }

  return (
    <div className="authpage">
      <div className="main-box">

        {/* Logo */}
        <img
          src={black_logo}
          id="logo"
          alt="Logo"
        />

        {/* Greeting */}
        <div className="greet-sec">

          <div className="welcome">
            {login
              ? "Yooo, welcome back!"
              : "Let's get you started!"}
          </div>

          <div className="logorsign">
            {login ? (
              <>
                First time here?
                <span onClick={toggleAuth}>
                  Sign up for free
                </span>
              </>
            ) : (
              <>
                Already have an account?
                <span onClick={toggleAuth}>
                  Login
                </span>
              </>
            )}
          </div>

        </div>

        {/* Form */}
        <form
          className="buttons"
          onSubmit={authentication}
        >

          {/* Username - Signup only */}
          {!login && (
            <input
              type="text"
              placeholder="your username"
              className="pill-input"
              value={username}
              autoComplete="username"
              required
              onChange={(e) => setUsername(e.target.value)}
            />
          )}

          {/* Email */}
          <input
            type="email"
            placeholder="your email"
            className="pill-input"
            value={email}
            autoComplete="email"
            required
            onChange={(e) => setEmail(e.target.value)}
          />

          {/* Password */}
          <div className="password-wrapper">

            <input
              type={showPassword ? "text" : "password"}
              placeholder="enter your password"
              className="password"
              value={password}
              autoComplete={
                login
                  ? "current-password"
                  : "new-password"
              }
              required
              onChange={(e) => setPassword(e.target.value)}
            />

            <button
              type="button"
              className="eye-button"
              onClick={() =>
                setShowPassword((prev) => !prev)
              }
              aria-label={
                showPassword
                  ? "Hide password"
                  : "Show password"
              }
            >
              {showPassword ? (
                <EyeOff size={17} strokeWidth={1.8} />
              ) : (
                <Eye size={17} strokeWidth={1.8} />
              )}
            </button>

          </div>

          {/* Submit */}
          <button type="submit">
            {login ? "Login" : "Sign Up"}
          </button>

        </form>

      </div>
    </div>
  );
};

export default Auth;