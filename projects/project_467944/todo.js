$(document).ready(function () {
  $("form").on("submit", function (event) {
    // Prevent the form from reloading the page
    event.preventDefault();
    // Get the value from the input field
    var todo = $("#todo").val();
    // Add the todo to the list
    $("<li>" + todo + "</li>").appendTo("#todo-list");
  });
});
