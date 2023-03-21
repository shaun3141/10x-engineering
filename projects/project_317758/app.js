// Bring in JQuery and Materialize
$(function () {
  var todos = [];
  // Render our Todos
  function renderTodos() {
    // Clear our the list first.
    $(".todo-list").html("");
    // Loop through our Todos and add them to the list.
    for (let i = 0; i < todos.length; i++) {
      $(".todo-list").append(`<p>${todos[i]}</p>`);
    }
  }
  // Watch for out form submission.
  $("form").submit(function (e) {
    // Stop the form from submitting (default behaviour).
    e.preventDefault();
    // Push our new Todo onto our list.
    todos.push($("input").val());
    // Clear out the input value field.
    $("input").val("");
    // Render our updated Todos.
    renderTodos();
  });
});
