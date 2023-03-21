import React, { useState } from "react";
import ToggleSwitch from "react-toggle-switch";

function DarkModeToggle(props) {
  const [isDarkMode, setIsDarkMode] = useState(false);

  function handleToggle() {
    setIsDarkMode(!isDarkMode);
    if (!isDarkMode) {
      document.body.classList.add("dark-mode");
    } else {
      document.body.classList.remove("dark-mode");
    }
    localStorage.setItem("isDarkMode", !isDarkMode);
  }

  return (
    <div className="right-align">
      <label className="switch-label">Dark Mode</label>
      <ToggleSwitch
        onClick={handleToggle}
        on={isDarkMode}
        className="dark-mode-toggle"
      />
    </div>
  );
}

export default DarkModeToggle;
