$(document).ready(function () {
  $("#add-todo").on("click", function () {
    const todoText = $("#todo-input").val().trim();
    if (todoText) {
      $("#todo-list").append(
        '<li class="collection-item">' + todoText + "</li>"
      );
      $("#todo-input").val("");
    }
  });
});
