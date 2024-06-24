## Author
- [John Shmulsky](https://github.com/jshmulsky)

# Algorithm Definition

![alt text](https://github.com/jshmulsky/SyphilisReactor/blob/main/Reactor-Flowchart.jpg?raw=true)

# Code Documentation

This code is an Azure Function, implemented as a  Python script, triggered by an HTTP request. It consists of two functions: `configureCodes` and `main`. The script performs configuration of codes and processing of the HTTP request. 

## Request Example

The URL endpoint will depend on the Azure Function App that hosts the script. 

### Headers
```json
{
    "Content-Type": "application/json",
    "x-functions-key":"<API KEY>"
}
```

### Body
```json
{
    "Investigations": [
        {
            "Test": "22461-8",
            "SpecimenDate": "20230407",
            "SpecimenSource": "BLOOD SPECIMEN",
            "Result": "11214006",
            "ResultValue": "REACTIVE"
        },
        {
            "Test": "31147-2",
            "SpecimenDate": "20230407",
            "SpecimenSource": "BLOOD SPECIMEN",
            "Result": "A",
            "ResultValue": "1:2"
        },
        {
            "Test": "47236-5",
            "SpecimenDate": "20220124",
            "SpecimenSource": "BLOOD SPECIMEN",
            "Result": "250510009",
            "ResultValue": "SYPHILIS ANTIBODY TITER MEASUREMENT"
        },
        {
            "Test": "22461-8",
            "SpecimenDate": "20220124",
            "SpecimenSource": "BLOOD SPECIMEN",
            "Result": "11214006",
            "ResultValue": "REACTIVE"
        },
        {
            "Test": "31147-2",
            "SpecimenDate": "20220124",
            "SpecimenSource": "BLOOD SPECIMEN",
            "Result": "A",
            "ResultValue": "1:4"
        }
    ],
    "Dispositions": [
        "PREVIOUSLY_TREATED",
    ],
    "Age": "1",
    "Gender": "Male"
}
```
### Response
```json
{
    "Disposition": "NEW",
    "DispositionDescription":"7a. Quantitative titer reported on current lab result (NEW)"
}
```

## Function Definition: configureCodes

This function is responsible for configuring the code tables used in the workflow. It reads data from CSV files and builds a code configuration dictionary.

- `table_dict` is a dictionary that maps table names to their corresponding CSV file names.
- The function initializes an empty `code_configuration` dictionary.
- It iterates over each `key` and `filename` pair in `table_dict`.
- Within each iteration, it opens the CSV file using `csv.reader` and skips the header row using `next(f_in)`.
- It then iterates over each line in the CSV file.
- For each line, it tries to extract the input value from the first column (`line[0]`).
- If the input value is not empty, it checks if the code set already exists in the `code_configuration` dictionary. If it does, it appends the input value to the existing code set. If the input value is not in lowercase, it appends the lowercase version to the code set as well.
- Finally, it updates the `code_configuration` dictionary with the updated code set for the corresponding table.
- The function returns the `code_configuration` dictionary.

## Function Definition: main

This function is the entry point for handling an HTTP request. It retrieves the JSON payload from the request, processes it using the `Reactor.process` function, and returns the result as an HTTP response.

- The function takes an `HttpRequest` object as the parameter.
- It calls the `get_json` method on the `req` object to retrieve the JSON data from the request and assigns it to the `json_in` variable.
- If the `code_config` global variable is `None`, it calls the `configureCodes` function to initialize the `code_config` dictionary with the code configurations.
- It then calls the `Reactor.process` function, passing in the `json_in` and `code_config` as arguments, and assigns the result to the `disposition` and `dispositionText` variables.
- The function builds a JSON response object with the "Disposition" and "DispositionText" values and assigns it to the `response` variable.
- It returns an `HttpResponse` object containing the `response` JSON object with the mime type set to "application/json".

## Code Execution

The code receives an HTTP request and extracts the JSON payload from the request. It initializes the code configurations by calling the `configureCodes` function. Then, it processes the JSON data using the `Reactor.process` function, and returns the result as an HTTP response with a JSON payload containing the "Disposition" and "DispositionText" values.

# Reactor Code Documentation

The Syphilis Algorithm is a Python code that processes an input JSON and applies a set of rules to determine the appropriate action for the given test results. The algorithm is used to categorize syphilis cases based on specific criteria.

## Function Definitions

### total_months(rdelta)

- This function takes a `relativedelta` object as input.
- It calculates the total number of months based on the `years` and `months` properties of the `rdelta` object.
- The total number of months is returned.

### getTiter(resultValue)

- This function takes a `resultValue` string as input.
- It retrieves the value after ":" in the `resultValue` string.
- The retrieved value is converted to an integer and returned.
- If an exception occurs during the conversion or the ":" character is not present in the `resultValue` string, 0 is returned.

### compare(x, y)

- This function takes two dictionaries, `x` and `y`, as input.
- It compares the values of the "SpecimenDate" key in both dictionaries.
- The function returns the difference between the two values as an integer.

### membership(val, codeset)

- This function takes a value `val` and a set `codeset` as input.
- It checks if the value is present in the set or its lowercase version.
- If the value is present, True is returned. Otherwise, False is returned.

### getSorted(input_json)

- This function takes an input JSON, `input_json`, as input.
- It retrieves the "Investigations" key from the `input_json`.
- The "Investigations" list is sorted based on the "SpecimenDate" key in descending order using the `compare` function as the key function for sorting.
- The sorted list is returned.

### getReactiveNonTreponemalTests(sorted_tests, code_config)

- This function takes a sorted list of tests, `sorted_tests`, and a code configuration dictionary, `code_config`, as inputs.
- It initializes a variable `most_recent_specimen` to None.
- It iterates over each test in the sorted list.
  - If the "SpecimenDate" of the test is less than `most_recent_specimen`, the iteration is stopped.
  - If the "Test" and "Result" of the test are present in the respective tables of the code configuration, or the "ResultValue" is a member of the specified table, the test is appended to the return list.
  - The "SpecimenDate" of the test is stored in `most_recent_specimen`.
- The return list of reactive non-treponemal tests is returned.

### seroconversion(sorted_tests, reactive_date, code_config)

- This function takes a sorted list of tests, `sorted_tests`, a reactive date as a string, `reactive_date`, and a code configuration dictionary, `code_config`, as inputs.
- It iterates over each test in the sorted list.
  - It calculates the month difference between the reactive date and the "SpecimenDate" of the test using the `relativedelta` function.
  - If the "SpecimenDate" of the test is less than the reactive date and the month difference is less than or equal to 18:
    - If the "Test" is present in the table 1 of the code configuration and the "Result" is present in table 4 of the code configuration, or the "ResultValue" is a member of table 8 of the code configuration, False is returned.
- True is returned if no test satisfies the above conditions.

### fourFoldTiterIncrease(reactive_non_treponemal_tests, sorted_tests, reactive_date, code_config)

- This function takes a list of reactive non-treponemal tests, `reactive_non_treponemal_tests`, a sorted list of tests, `sorted_tests`, a reactive date as a string, `reactive_date`, and a code configuration dictionary, `code_config`, as inputs.
- It initializes two lists, `rnttTiter` and `ptTiter`, to store the titers.
- It iterates over each test in the reactive non-treponemal tests list and appends the titer value (obtained using the `getTiter` function) to `rnttTiter`.
- It iterates over each test in the sorted list.
  - It calculates the month difference between the reactive date and the "SpecimenDate" of the test using the `relativedelta` function.
  - If the "SpecimenDate" of the test is less than the reactive date and the month difference is less than or equal to 18:
    - If the "Test" is present in table 1 of the code configuration and the "ResultValue" is present in table 6 of the code configuration, the titer value (obtained using the `getTiter` function) is appended to `ptTiter`.
- The maximum titer value in `rnttTiter` is divided by the minimum titer value in `ptTiter`, and if the result is greater than or equal to 4, True is returned. Otherwise, False is returned.

### femaleUnder50Titer8Previous6Months(input_json, reactive_non_treponemal_tests, sorted_tests, reactive_date, code_config)

- This function takes an input JSON, `input_json`, a list of reactive non-treponemal tests, `reactive_non_treponemal_tests`, a sorted list of tests, `sorted_tests`, a reactive date as a string, `reactive_date`, and a code configuration dictionary, `code_config`, as inputs.
- It checks if the gender in the input JSON is "Female", the age is not empty, and the age is less than 50.
- If the above conditions are satisfied, it iterates over each test in the reactive non-treponemal tests list and checks if the titer value (obtained using the `getTiter` function) is greater than 8.
- It also iterates over each test in the sorted list.
  - It calculates the month difference between the reactive date and the "SpecimenDate" of the test using the `relativedelta` function.
  - If the "SpecimenDate" of the test is less than the reactive date and the month difference is greater than or equal to 6, and the "Test" is present in table 1 of the code configuration and the "ResultValue" is present in table 6 of the code configuration, True is returned.
- False is returned if no test satisfies the above conditions.

### currentTiter32Previous1Year(reactive_non_treponemal_tests, sorted_tests, reactive_date, code_config)

- This function takes a list of reactive non-treponemal tests, `reactive_non_treponemal_tests`, a sorted list of tests, `sorted_tests`, a reactive date as a string, `reactive_date`, and a code configuration dictionary, `code_config`, as inputs.
- It checks if any test in the reactive non-treponemal tests list has a titer value (obtained using the `getTiter` function) greater than 32.
- It also iterates over each test in the sorted list.
  - It calculates the month difference between the reactive date and the "SpecimenDate" of the test using the `relativedelta` function.
  - If the "SpecimenDate" of the test is less than the reactive date and the month difference is between 12 and 18 (inclusive), and the "Test" is present in table 1 of the code configuration and the "ResultValue" is present in table 6 of the code configuration, True is returned.
- False is returned if no test satisfies the above conditions.

### quantitativeTiterOnPrevious(sorted_tests, reactive_date, code_config)

- This function takes a sorted list of tests, `sorted_tests`, a reactive date as a string, `reactive_date`, and a code configuration dictionary, `code_config`, as inputs.
- It iterates over each test in the sorted list.
  - It calculates the month difference between the reactive date and the "SpecimenDate" of the test using the `relativedelta` function.
  - If the "SpecimenDate" of the test is less than the reactive date and the month difference is less than or equal to 18, and the "Test" is present in table 1 of the code configuration and the "ResultValue" is present in table 6 of the code configuration, True is returned.
- False is returned if no test satisfies the above conditions.

### quantitativeTiterReported(reactive_non_treponemal_tests, code_config)

- This function takes a list of reactive non-treponemal tests, `reactive_non_treponemal_tests`, and a code configuration dictionary, `code_config`, as inputs.
- It iterates over each test in the reactive non-treponemal tests list.
  - If the "Test" is present in table 1 of the code configuration and the "ResultValue" is present in table 6 of the code configuration, True is returned.
- False is returned if no test satisfies the above conditions.

### previouslyUnableToLocate(input_json)

- This function takes an input JSON, `input_json`, as input.
- It checks if the "Dispositions" in the input JSON contains the value "UNABLE_TO_LOCATE" or "REFUSED_EXAMINATION_TREATMENT".
- True is returned if either of the values is present. Otherwise, False is returned.

### priorSyphilisNTTest(sorted_tests, reactive_date, code_config)

- This function takes a sorted list of tests, `sorted_tests`, a reactive date as a string, `reactive_date`, and a code configuration dictionary, `code_config`, as inputs.
- It iterates over each test in the sorted list.
  - It calculates the month difference between the reactive date and the "SpecimenDate" of the test using the `relativedelta` function.
  - If the "SpecimenDate" of the test is less than the reactive date and the month difference is less than or equal to 18, and the "Test" is present in table 1 of the code configuration, True is returned.
- False is returned if no test satisfies the above conditions.

### penultimateNegativeTreponemal(sorted_tests, reactive_date, code_config)

- This function takes a sorted list of tests, `sorted_tests`, a reactive date as a string, `reactive_date`, and a code configuration dictionary, `code_config`, as inputs.
- It initializes a variable `penultimateDate` to None.
- It iterates over each test in the sorted list.
  - If the "SpecimenDate" of the test is less than the reactive date and the number of days between the reactive date and the "SpecimenDate" is less than or equal to 14:
    - If `penultimateDate` is not None and greater than the "SpecimenDate" of the test, the iteration is stopped.
    - `penultimateDate` is set to the "SpecimenDate" of the test.
    - If the "Test" is present in table 2 of the code configuration and the "Result" is present in table 5 of the code configuration, or the "ResultValue" is a member of table 9 of the code configuration, True is returned.
- False is returned if no test satisfies the above conditions.

### ntWithin14Days(input_json, reactive_date, code_config)

- This function takes an input JSON, `input_json`, a reactive date as a string, `reactive_date`, and a code configuration dictionary, `code_config`, as inputs.
- It checks if any test in the input JSON was sampled within 14 days before the reactive date and satisfies the conditions for being a non-reactive treponemal test (present in table 2 of the code configuration and having a result present in table 5 or a result value that is a member of table 9).
- True is returned if such a test is found. Otherwise, False is returned.

### lessThanOne(input_json)

- This function takes an input JSON, `input_json`, as input.
- It checks if the "Age" in the input JSON is not empty and less than or equal to 1.
- True is returned if the above condition is satisfied. Otherwise, False is returned.

### ntSampledCSFOrChord(reactive_non_treponemal_tests, code_config)

- This function takes a list of reactive non-treponemal tests, `reactive_non_treponemal_tests`, and a code configuration dictionary, `code_config`, as inputs.
- It checks if any test in the list has a "Test" present in table 3 of the code configuration or a "SpecimenSource" present in table 7 of the code configuration.
- True is returned if such a test is found. Otherwise, False is returned.

### process(input_json, code_config)

- This function takes an input JSON, `input_json`, and a code configuration dictionary, `code_config`, as inputs.
- It first calls the `getSorted` function to obtain a sorted list of tests from the input JSON.
- It then calls the `getReactiveNonTreponemalTests` function to obtain a list of reactive non-treponemal tests from the sorted list.
- If the length of the reactive non-treponemal tests list is 0, it returns a tuple with the action "NO_ACTION" and an appropriate message.
- It retrieves the reactive date from the first test in the reactive non-treponemal tests list.
- It checks various conditions using the functions defined above to determine the appropriate action.
- If a condition is satisfied, it returns a tuple with the corresponding action and an appropriate message.
- If no conditions are satisfied, it returns a tuple with the action "ADMINISTRATIVELY_CLOSE" and a message indicating that all steps through the algorithm have been completed.

## Code Execution

The code defines various functions that are used to process an input JSON and apply a set of rules to determine the appropriate action based on the test results. The `process` function is called with the input JSON and code configuration as arguments to initiate the processing of the data. The function checks various conditions and returns a tuple with the determined action and an appropriate message based on the conditions.

## Thank you

This project was made possible through the efforts of many people. 

| Name              |
| ----------------- | 
| Anne Bergman      | 
| Saugat Karki      | 
| Alejandro Perez   | 
| James Matthias    |
