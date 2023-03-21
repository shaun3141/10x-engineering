// Wait until the page is fully loaded
$(document).ready(function () {
  // Get handle to the form
  var form = $("#todo-form");

  // Handle form submission
  form.submit(function (event) {
    // Prevent default action of the form
    event.preventDefault();

    // Get the text entered by the user
    var todoEntry = $("#todo-item").val();

    // Add a new list item with the todoEntry as its text
    $("#todo-list").append("<li>" + todoEntry + "</li>");

    // Reset the form
    form[0].reset();
  });
});
