$(document).ready(function () {
  $("#addTodoItem").click(function () {
    var newTodo = $("#newTodoItem").val();
    $(".collection").append('<li class="collection-item">' + newTodo + "</li>");
    $("#newTodoItem").val("");
  });
});
