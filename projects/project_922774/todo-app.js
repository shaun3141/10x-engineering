$(document).ready(function () {
  $("#todo-form").on("submit", function (event) {
    event.preventDefault();
    let todoText = $("#todo-input").val().trim();
    if (todoText) {
      $("#todo-list").append(
        `<li class="collection-item"><div>${todoText}<a class="secondary-content"><i class="material-icons delete-todo">delete</i></a></div></li>`
      );
      $("#todo-input").val("");
    }
  });

  $("#todo-list").on("click", ".delete-todo", function () {
    $(this).closest("li").remove();
  });
});
