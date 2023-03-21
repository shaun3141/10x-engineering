// Add code to handle note submit event
function handleNoteSubmit(e) {
  e.preventDefault();
  const noteInput = document.getElementById("note-input");
  const noteValue = noteInput.value.trim();
  const taskId = noteInput.dataset.taskId;

  saveNotesToLocalStorage(taskId, noteValue); // Add code to save notes to localStorage
  renderTasks(currentTab);
  closeModal();
}

// Add event listener to note form
const noteForm = document.getElementById("note-form");
noteForm.addEventListener("submit", handleNoteSubmit);
