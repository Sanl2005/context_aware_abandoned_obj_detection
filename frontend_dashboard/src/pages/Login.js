import React, { useState, useContext, useEffect } from "react";
import { AuthContext } from "../auth/AuthContext";
import { useNavigate } from "react-router-dom";
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import AppleSignin from 'react-apple-signin-auth';
import { jwtDecode } from 'jwt-decode';
import "./Login.css";

export function LoginComponent() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [ripples, setRipples] = useState([]);
  const [floatingShapes, setFloatingShapes] = useState([]);
  const { login, loginWithOAuth } = useContext(AuthContext);
  const navigate = useNavigate();

  // Generate floating shapes on mount
  useEffect(() => {
    const shapes = [];
    for (let i = 0; i < 15; i++) {
      shapes.push({
        id: i,
        x: Math.random() * 100,
        y: Math.random() * 100,
        size: Math.random() * 80 + 40,
        delay: Math.random() * 5,
        duration: Math.random() * 10 + 15,
        type: ['circle', 'square', 'triangle'][Math.floor(Math.random() * 3)]
      });
    }
    setFloatingShapes(shapes);
  }, []);

  // Handle mouse movement for parallax effect
  useEffect(() => {
    const handleMouseMove = (e) => {
      const shapes = document.querySelectorAll('.floating-shape');
      const x = e.clientX / window.innerWidth;
      const y = e.clientY / window.innerHeight;

      shapes.forEach((shape, index) => {
        const speed = (index + 1) * 0.5;
        const moveX = (x - 0.5) * speed * 20;
        const moveY = (y - 0.5) * speed * 20;
        shape.style.transform = `translate(${moveX}px, ${moveY}px)`;
      });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const createRipple = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const newRipple = {
      x,
      y,
      id: Date.now()
    };

    setRipples(prev => [...prev, newRipple]);
    setTimeout(() => {
      setRipples(prev => prev.filter(r => r.id !== newRipple.id));
    }, 600);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login(username, password);
      navigate("/");
    } catch (err) {
      setError(err.message || "Invalid credentials. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSuccess = async (credentialResponse) => {
    setError("");
    setLoading(true);

    try {
      const decoded = jwtDecode(credentialResponse.credential);
      const userInfo = {
        email: decoded.email,
        name: decoded.name,
        picture: decoded.picture,
      };

      await loginWithOAuth('google', credentialResponse.credential, userInfo);
      navigate("/");
    } catch (err) {
      setError("Google sign-in failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleError = () => {
    setError("Google sign-in was unsuccessful. Please try again.");
  };

  const handleAppleSuccess = async (response) => {
    setError("");
    setLoading(true);

    try {
      const decoded = jwtDecode(response.authorization.id_token);
      const userInfo = {
        email: decoded.email,
        name: response.user?.name ?
          `${response.user.name.firstName} ${response.user.name.lastName}` :
          decoded.email,
      };

      await loginWithOAuth('apple', response.authorization.id_token, userInfo);
      navigate("/");
    } catch (err) {
      setError("Apple sign-in failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleAppleError = (error) => {
    console.error('Apple sign-in error:', error);
    setError("Apple sign-in was unsuccessful. Please try again.");
  };

  return (
    <div className="login-page">
      <div className="login-background">
        <div className="gradient-sphere sphere-1"></div>
        <div className="gradient-sphere sphere-2"></div>
        <div className="gradient-sphere sphere-3"></div>

        {/* Floating interactive shapes */}
        {floatingShapes.map(shape => (
          <div
            key={shape.id}
            className={`floating-shape shape-${shape.type}`}
            style={{
              left: `${shape.x}%`,
              top: `${shape.y}%`,
              width: `${shape.size}px`,
              height: `${shape.size}px`,
              animationDelay: `${shape.delay}s`,
              animationDuration: `${shape.duration}s`
            }}
          ></div>
        ))}
      </div>

      <div className="login-container">
        <div className="login-card" onClick={createRipple}>
          {ripples.map(ripple => (
            <span
              key={ripple.id}
              className="ripple"
              style={{
                left: ripple.x,
                top: ripple.y
              }}
            ></span>
          ))}

          <div className="login-header">
            <div className="logo-container">
              <div className="logo-icon-wrapper">
                <span className="logo-icon"></span>
                <div className="icon-glow"></div>
              </div>
              <h1 className="logo-text">SmartLook</h1>
            </div>
            <p className="login-subtitle">Secure Access Portal</p>
            <div className="subtitle-underline"></div>
          </div>

          <form onSubmit={handleSubmit} className="login-form">
            {error && (
              <div className="error-banner">
                <span className="error-icon">⚠️</span>
                <span>{error}</span>
              </div>
            )}

            <div className="form-group">
              <label htmlFor="username" className="form-label">
                <span className="label-icon">👤</span>
                Username
              </label>
              <div className="input-wrapper">
                <input
                  id="username"
                  type="text"
                  className="form-input"
                  placeholder="Enter your username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  autoFocus
                />
                <div className="input-border"></div>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="password" className="form-label">
                <span className="label-icon">🔒</span>
                Password
              </label>
              <div className="input-wrapper">
                <input
                  id="password"
                  type="password"
                  className="form-input"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <div className="input-border"></div>
              </div>
            </div>

            <button
              type="submit"
              className="login-button"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Authenticating...
                </>
              ) : (
                <>
                  <span>Sign In</span>
                  <span className="button-arrow">→</span>
                </>
              )}
              <div className="button-shine"></div>
            </button>

            {/* OAuth Divider */}
            <div className="oauth-divider">
              <span className="divider-line"></span>
              <span className="divider-text">Or continue with</span>
              <span className="divider-line"></span>
            </div>

            {/* OAuth Buttons */}
            <div className="oauth-buttons">
              <GoogleLogin
                onSuccess={handleGoogleSuccess}
                onError={handleGoogleError}
                useOneTap={false}
                theme="filled_blue"
                size="large"
                text="continue_with"
                shape="rectangular"
                logo_alignment="left"
                width="100%"
              />

              <AppleSignin
                authOptions={{
                  clientId: 'com.sentineleye.service',
                  scope: 'email name',
                  redirectURI: window.location.origin,
                  state: 'state',
                  nonce: 'nonce',
                  usePopup: true,
                }}
                uiType="dark"
                className="apple-auth-btn"
                onSuccess={handleAppleSuccess}
                onError={handleAppleError}
                buttonExtraChildren="Continue with Apple"
              />
            </div>
          </form>
        </div>

        <div className="security-badge">
          <span className="badge-icon">🔐</span>
          <span className="badge-text">Secured with end-to-end encryption</span>
        </div>
      </div>
    </div>
  );
}

// Wrap with Google OAuth Provider
export default function Login() {
  // Get Google Client ID from environment variable or use placeholder
  // To configure: Create a .env file and set REACT_APP_GOOGLE_CLIENT_ID
  // See OAUTH_SETUP_GUIDE.md for detailed instructions
  const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID || "YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com";

  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <LoginComponent />
    </GoogleOAuthProvider>
  );
}
