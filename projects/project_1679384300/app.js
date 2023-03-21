$(document).ready(function () {
  var todoList = $("#todo-list");
  var todoForm = $("#todo-form");
  var todoInput = $("#todo");
  var todos = [];

  todoForm.submit(function (event) {
    event.preventDefault();
    var newTodo = todoInput.val();
    if (newTodo.length > 0) {
      todos.push(newTodo);
      updateTodoList();
      todoInput.val("");
    }
  });

  function updateTodoList() {
    todoList.empty();
    for (var i = todos.length - 1; i >= 0; i--) {
      var todoItem = $("<li>").addClass("collection-item").text(todos[i]);
      todoList.append(todoItem);
    }
  }
});
