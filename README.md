# Medication Schedule Maker (English + Arabic)

**Author:** Arwa Hatem Ibrahim

## The idea
Many patients forget when and how to take their medicines, and many leaflets are only in English.
This small tool reads a CSV file with the medicines written by the doctor and makes a clean,
printable schedule in **English and Arabic**: a medicine list, plus a "My day" table with tick boxes
for morning, noon, evening, and bedtime.

It does **not** choose doses or give medical advice. It only copies the prescriber's instructions.

## Files
| File | What it is |
|---|---|
| `med_schedule.py` | The program (Python standard library only, no installs) |
| `medications.csv` | Example input file |
| `sample_schedule.html` / `sample_schedule.pdf` | Example output |

## How to use
1. Edit `medications.csv` (one row per medicine).
2. Run: `python med_schedule.py medications.csv --patient "Name" --pharmacist "Name"`
3. Open `schedule.html` in a browser and print it, or save it as PDF.

## CSV columns
`drug, amount, unit, morning, noon, evening, bedtime, instructions, days, notes`

- **amount + unit**: dose each time (for example `1` + `tablet`). Units: tablet, capsule, ml, puff, drop, unit.
- **morning / noon / evening / bedtime**: put the number of doses (`1`, `0.5`, `1/2`) or leave empty.
- **instructions**: one or more, separated by `;` - with_food, after_food, before_food, before_breakfast, empty_stomach, at_bedtime, with_water.
- **days**: how many days (empty = ongoing). **notes**: any extra text.

## What the code does
1. `read_medicines()` reads the CSV and checks for mistakes (empty names, unknown units, no time of day).
2. `dose_in_english()` and `dose_in_arabic()` write the dose in both languages (with Arabic plural forms).
3. `build_page()` builds the HTML page (English left-to-right, Arabic right-to-left).

## Limits
- The example patient and medicines are made up. This is not a real prescription.
- A pharmacist must check every schedule before it is given to a patient.
- It does not check drug interactions or doses.

## Ideas to improve
- Add more languages and more instructions.
- Add a weekly tick chart and larger text for older patients.
- Read the data from an Excel file.

## Note
I built this project with help from AI tools and tested it on my own examples.
