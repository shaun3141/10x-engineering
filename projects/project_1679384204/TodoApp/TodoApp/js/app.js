$(document).ready(function () {
  // initialize the materialize components
  M.AutoInit();

  // handle form submission on submit button click and enter key press
  $("#todo-form").submit(function (e) {
    e.preventDefault();
    addTodo();
  });
  $("#todo-input").on("keypress", function (e) {
    if (e.which === 13) {
      addTodo();
    }
  });

  // helper function to add a new todo to the list
  function addTodo() {
    var todoInput = $("#todo-input");
    var todoList = $("#todo-list");
    var todoText = todoInput.val();
    if (todoText) {
      var todoHtml =
        '<li class="collection-item">' +
        todoText +
        ' <a href="#!" class="secondary-content"><i class="material-icons">delete</i></a></li>';
      todoList.append(todoHtml);
      todoInput.val("");
      // add event listener to newly added delete button
      $("#todo-list li:last-child a").click(function () {
        $(this).parent().remove();
      });
      // re-initialize materialize tooltip
      M.Tooltip.init(document.querySelectorAll(".tooltipped"));
    }
  }
});
