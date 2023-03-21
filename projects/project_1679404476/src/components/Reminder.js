import React from "react";
function Reminder() {
  return (
    <div className="reminder-modal">
      {" "}
      <form>
        {" "}
        <label>Set Reminder:</label>{" "}
        <input
          type="datetime-local"
          id="reminder-time"
          name="reminder-time"
        ></input>{" "}
        <button type="submit" className="btn">
          Set
        </button>{" "}
      </form>{" "}
    </div>
  );
}
export default Reminder;
