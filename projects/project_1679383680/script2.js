// Add code to save and load task notes from localStorage.

function saveNotesToLocalStorage(id, note) {
  let tasks = JSON.parse(localStorage.getItem("tasks")) || [];
  tasks.forEach((task) => {
    if (task.id === id) task.notes = note;
  });
  localStorage.setItem("tasks", JSON.stringify(tasks));
}

function loadNotesFromLocalStorage(id) {
  let tasks = JSON.parse(localStorage.getItem("tasks")) || [];
  let selectedTask = tasks.find((task) => task.id === id);
  return selectedTask ? selectedTask.notes : "";
}

// Add code to update the task object when note is added

function handleNoteSubmit(e) {
  e.preventDefault();
  const noteInput = document.getElementById("note-input");
  const noteValue = noteInput.value.trim();
  const taskId = noteInput.dataset.taskId;

  const currentTask = taskList.find((task) => task.id === taskId);
  currentTask.notes = noteValue;
  saveTasksToLocalStorage();
  renderTasks(currentTab);
  closeModal();
}
