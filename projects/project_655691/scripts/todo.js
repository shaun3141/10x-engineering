const todos = [];

// Add a todo item to the array
const addToDo = () => todos.push({ title: "New Todo" });

// Delete a todo item from the array
const deleteToDo = (i) => todos.splice(i, 1);

// Render the array of todos to the DOM
const renderToDos = () => {
  const todosListEl = document.getElementById("todoList");
  todosListEl.innerHTML = "";
  todos.forEach((todo, i) => {
    const itemEl = document.createElement("li");
    itemEl.innerText = todo.title;

    const deleteBtn = document.createElement("button");
    deleteBtn.innerText = "X";
    deleteBtn.addEventListener("click", (e) => deleteToDo(i));

    itemEl.appendChild(deleteBtn);
    todosListEl.appendChild(itemEl);
  });
};

// Init
renderToDos();

// Add form
const addFormEl = document.createElement("form");
addFormEl.addEventListener("submit", (e) => {
  e.preventDefault();
  addToDo();
  renderToDos();
});

const addInputEl = document.createElement("input");
addInputEl.type = "text";
addInputEl.placeholder = "New Todo..";
addFormEl.appendChild(addInputEl);

const addBtnEl = document.createElement("button");
addBtnEl.type = "submit";
addBtnEl.innerText = "Add Todo";
addFormEl.appendChild(addBtnEl);

document.body.appendChild(addFormEl);
