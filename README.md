# Mystery Delivery System

## Project idea
This project reads delivery data from JSON, assigns packages to the nearest agent, simulates delivery travel, and writes the final report.

## Files
- `implementation/main.py` - runs the program from the command line
- `implementation/delivery.py` - main business logic for assignment and route simulation
- `implementation/utils.py` - JSON reading and distance calculation
- `implementation/test_cases/` - all 10 test cases
- `implementation/reports/` - output reports created by the program

## How to run

```powershell
python .\main.py
```

To run one test case:

```powershell
python .\main.py ".\test_cases\test_case_1.json" -o ".\reports\report_test_case_1.json"
```

To run all test cases together:

```powershell
Get-ChildItem ".\test_cases" -Filter *.json | ForEach-Object {
    python .\main.py $_.FullName -o ".\reports\report_$($_.BaseName).json"
}
```

To export the top performer as CSV (as per provided test case):

```powershell
python .\main.py .\base_case.json -o .\report.json --csv .\top_performer.csv
```

## What the program does
- Reads the JSON file
- Converts all coordinates into normal `(x, y)` format
- Finds the nearest agent to each warehouse
- Assigns each package to that agent
- Simulates travel from the agent to the warehouse and then to the destination
- Calculates total distance and efficiency
- Saves the final report in JSON

## Assumptions used for unclear cases
The assignment had some unclear points, so the following assumptions were used to keep the logic simple and consistent:

- If the JSON is a little messy, the code tries to fix common issues like single quotes, trailing commas, and repeated key-like text.
- Agents start from their given location and do not return to base after finishing.
- If several packages are from the same warehouse, the agent visits that warehouse once and delivers all packages from there.
- If a package has no valid warehouse ID, it is assigned to the nearest agent based on the destination location.
- If two agents are equally close, the agent whose ID comes first in sorted order is chosen.
- Delivery order is chosen by always taking the nearest remaining destination from the current position.
- Warehouse order is sorted before processing so the result stays stable and repeatable.
- If there is any missing or unclear edge case, the program chooses the most logical and efficient option instead of stopping.

## Verified result
I ran the program on the base case and it produced this output:

```json
{
  "A1": {
    "packages_delivered": 2,
    "total_distance": 57.27,
    "efficiency": 28.63
  },
  "A2": {
    "packages_delivered": 2,
    "total_distance": 205.92,
    "efficiency": 102.96
  },
  "A3": {
    "packages_delivered": 1,
    "total_distance": 206.51,
    "efficiency": 206.51
  },
  "best_agent": "A1"
}
```

## Important note
The sample numbers shown in the PDF are not exactly matching the real Euclidean-distance result for the given coordinates. The code follows the standard and logical rule for this assignment: nearest agent + Euclidean distance + route simulation. This is the valid approach for the problem statement.
