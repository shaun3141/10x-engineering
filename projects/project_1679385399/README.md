## Feature Request

You will be implementing the following feature request:
**Custom Calculation** - Allow users to define their own mathematical operation to be performed on the input list of numbers.

Add a text input field where users can input a mathematical expression using the input list of numbers (e.g. lambda x: x \* 2 + 5). Upon submission, perform the custom calculation on the input list of numbers and return the result.

Please remember the following application constraints:

- This app will not have a database.
- This app will not have the ability to do user authentication.
- This app will be a stand-alone web application
- This app will be deployed to Vercel
- This app should not need to be configured to run (for example, no environment variables)
- This app should not use any 3rd party APIs (OAuth, Stripe, Databases, etc.)

### Example Usage

Enter the operation you would like to perform (sum, product, or custom): custom
Enter a mathematical expression using x to represent each number in the list: x\*\*2-1
Enter a comma-separated list of numbers: 1,2,3,4
[0.0, 3.0, 8.0, 15.0]
