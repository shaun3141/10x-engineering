$(document).ready(function () {
  $("#operation").change(function () {
    if ($(this).val() === "custom") {
      $("#customExpression").show();
    } else {
      $("#customExpression").hide();
    }
  });

  $("#calculateButton").click(function () {
    var operation = $("#operation").val();
    var numbers = $("#numberList").val().split(",").map(Number);
    var expression = "";
    var result = "";

    if (operation === "custom") {
      expression = $("#expression").val();
      result = calculate(numbers, expression);
    } else {
      result = calculate(numbers, operation);
    }

    var resultString = "Result: " + result.toFixed(2);
    $("#result").html(resultString);
  });
});

function calculate(numbers, operation) {
  if (operation === "sum") {
    return numbers.reduce(function (total, num) {
      return total + num;
    }, 0);
  } else if (operation === "product") {
    return numbers.reduce(function (total, num) {
      return total * num;
    }, 1);
  } else {
    var expression = operation.replace(/x/g, "numbers[i]");
    var result = 0;
    for (var i = 0; i < numbers.length; i++) {
      result += eval(expression);
    }
    return result;
  }
}
