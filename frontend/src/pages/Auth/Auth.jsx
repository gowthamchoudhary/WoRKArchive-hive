import React, { useState } from "react";
import black_logo from "../../assets/black_logo_logs.png";

const Auth = () => {
  const [login, setLogin] = useState(true);

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);

  async function authentication(e) {
    e.preventDefault();

    if (login) {
      console.log("Login:", {
        email,
        password,
      });
    } else {
      console.log("Signup:", {
        username,
        email,
        password,
      });
    }
  }

  function toggleAuth() {
    setLogin(!login);

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

            <button
              type="button"
              className="eye-button"
              onClick={() => setShowPassword(!showPassword)}
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? "🙈" : "👁️"}
            </button>
          </div>

          <button type="submit">{login ? "Login" : "Sign Up"}</button>
        </form>
      </div>
    </div>
  );
};

export default Auth;
