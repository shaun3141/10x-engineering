// modify main function to include number base conversion
function sumNumbers() {
  let numbers = document
    .getElementById("numberInput")
    .value.split(",")
    .map((num) => num.trim());
  let base = parseInt(document.getElementById("baseSelect").value);
  let convertedNumbers = numbers.map((num) => convertToDecimal(num, base));
  let sum = convertedNumbers.reduce((a, b) => a + b, 0);
  let total = convertToBase(sum, base);
  let groups = groupNumbers(convertedNumbers, base);
  renderElements(groups, total);
}
