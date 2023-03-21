$(document).ready(function () {
  $("#todo-input").keydown(function (event) {
    if (event.keyCode === 13) {
      // Enter key
      var todoContent = $(this).val();
      $(this).val("");
      if (todoContent !== "") {
        $("<li>")
          .addClass("collection-item")
          .text(todoContent)
          .appendTo(".collection");
      }
    }
  });
});
