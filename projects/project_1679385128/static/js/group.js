// Logic to group numbers and calculate
// the sum of each group

function groupNumbers(numbers, size) {
  let groups = [];
  let sum = 0;
  for (let i = 0; i < numbers.length; i++) {
    sum += numbers[i];
    if ((i + 1) % size === 0) {
      groups.push(sum);
      sum = 0;
    }
  }
  if (sum !== 0) {
    groups.push(sum);
  }
  return groups;
}
