$(document).ready(function () {
  var $todoInput = $(
    '<input type="text" placeholder="Enter a task" id="todo-input">'
  );
  var $todoSubmit = $('<button class="btn">Add Task</button>');
  var $todoList = $('<ul class="collection"></ul>');

  $("body").append($todoInput);
  $("body").append($todoSubmit);
  $("body").append($todoList);

  $todoSubmit.click(function () {
    var task = $todoInput.val().trim();
    if (task.length > 0) {
      $todoList.append('<li class="collection-item">' + task + "</li>");
      $todoInput.val("");
    }
  });

  $todoList.on("click", "li", function () {
    $(this).toggleClass("completed");
  });
});
