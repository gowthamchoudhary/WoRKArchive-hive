import React, { useState } from "react";
import { Eye, EyeOff } from "lucide-react";

import black_logo from "../../assets/black_logo_logs.png";
import "./Auth.css";
import { loginUser, registerUser } from "../../api/auth";

const Auth = () => {
  const [login, setLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);

  async function authentication(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    setMessage("");
    try {
      if (login) {
        const response = await loginUser(username, password);
        console.log("response", response);
        setMessage("logged in successfully");
      } else {
        const response = await registerUser(username, email, password);
        console.log("response", response);
        setMessage("Account created succefully");
        setUsername("");
        setEmail("");
        setPassword("");
      }
    } catch (error) {
      console.error("auth error", error);
      if (error.response) {
        setError(error.response.data?.detail || "Something went wrong");
      } else if (error.request) {
        setError("Cannot connect to the server");
      } else {
        setError("Something went wrong");
      }
    } finally {
      setLoading(false);
    }
  }

  function toggleAuth() {
    setLogin((prev) => !prev);

    setUsername("");
    setEmail("");
    setPassword("");

    setShowPassword(false);
  }

  return (
    <div className="authpage">
      <div className="main-box">
        <img src={black_logo} id="logo" alt="Logo" />

        <div className="greet-sec">
          <div className="welcome">
            {login ? "Yooo, welcome back!" : "Let's get you started!"}
          </div>

          <div className="logorsign">
            {login ? (
              <>
                First time here?
                <span onClick={toggleAuth}>Sign up for free</span>
              </>
            ) : (
              <>
                Already have an account?
                <span onClick={toggleAuth}>Login</span>
              </>
            )}
          </div>
        </div>

        <form className="buttons" onSubmit={authentication}>
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

          <input
            type="email"
            placeholder="your email"
            className="pill-input"
            value={email}
            autoComplete="email"
            required
            onChange={(e) => setEmail(e.target.value)}
          />

          <div className="password-wrapper">
            <input
              type={showPassword ? "text" : "password"}
              placeholder="enter your password"
              className="password"
              value={password}
              autoComplete={login ? "current-password" : "new-password"}
              required
              onChange={(e) => setPassword(e.target.value)}
            />
            {error && <p className="auth-error">{error}</p>}
            {message && <p className="auth-success">{message}</p>}

            <button
              type="button"
              className="eye-button"
              onClick={() => setShowPassword((prev) => !prev)}
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? (
                <EyeOff size={17} strokeWidth={1.8} />
              ) : (
                <Eye size={17} strokeWidth={1.8} />
              )}
            </button>
          </div>

          <button type="submit" disabled={loading}>
            {loading
              ? login
                ? "Logging in..."
                : "Creating account..."
              : login
                ? "Login"
                : "Sign Up"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Auth;
