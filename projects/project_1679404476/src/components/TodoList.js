import { useState } from "react";
import "./TodoList.css";
import TodoItem from "./TodoItem.js";
import Reminder from "./Reminder.js";
function TodoList({ items, setItems }) {
  const [todoPriorities, setTodoPriorities] = useState(
    items.map((item) => item.key)
  );
  const [showReminder, setShowReminder] = useState(false);
  return (
    <div>
      {" "}
      {showReminder ? <Reminder /> : null}{" "}
      <ul
        className="collection"
        onDragOver={(e) => {
          e.preventDefault();
        }}
        onDrop={(e) => {
          e.preventDefault();
          const newIndex = e.target.dataset.index;
          const draggedIndex = e.dataTransfer.getData("text/plain");
          const newPriorities = Array.from(todoPriorities);
          const [removed] = newPriorities.splice(draggedIndex, 1);
          newPriorities.splice(newIndex, 0, removed);
          setTodoPriorities(newPriorities);
          setItems(
            items.sort((a, b) => {
              const aIndex = newPriorities.indexOf(a.key);
              const bIndex = newPriorities.indexOf(b.key);
              return aIndex - bIndex;
            })
          );
        }}
      >
        {" "}
        {items.map((item, index) => {
          return (
            <li
              key={item.key}
              draggable="true"
              onDragStart={(e) => {
                e.dataTransfer.setData("text/plain", index);
              }}
              onDragOver={(e) => {
                e.preventDefault();
              }}
              onDrop={(e) => {
                const newIndex = e.target.dataset.index;
                const draggedIndex = e.dataTransfer.getData("text/plain");
                const newPriorities = Array.from(todoPriorities);
                const [removed] = newPriorities.splice(draggedIndex, 1);
                newPriorities.splice(newIndex, 0, removed);
                setTodoPriorities(newPriorities);
                setItems(
                  items.sort((a, b) => {
                    const aIndex = newPriorities.indexOf(a.key);
                    const bIndex = newPriorities.indexOf(b.key);
                    return aIndex - bIndex;
                  })
                );
              }}
              data-index={index}
            >
              {" "}
              <TodoItem item={item} setItems={setItems} />{" "}
              <button
                className="reminder-button"
                onClick={() => setShowReminder(true)}
              >
                Set Reminder
              </button>{" "}
            </li>
          );
        })}{" "}
      </ul>{" "}
    </div>
  );
}
export default TodoList;
