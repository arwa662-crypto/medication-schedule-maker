"""
Medication Schedule Maker (English + Arabic)
Author: Arwa Hatem Ibrahim

Idea: Patients often forget when and how to take their medicines.
This tool reads a simple CSV file (the medicines written by the doctor)
and makes a clean, printable schedule in English and Arabic.

It does NOT choose doses or give medical advice.
It only copies what the doctor or pharmacist wrote, in a clear way.

How to use:
    python med_schedule.py medications.csv --patient "Name" --pharmacist "Name"
Then open schedule.html in a browser and print it (or save as PDF).
Only the Python standard library is needed.
"""

import argparse
import csv
import html
import sys
from datetime import date

# ---------- Settings you can change ----------

# Times of day: key -> (English name, Arabic name, clock time)
SLOTS = {
    "morning": ("Morning", "الصباح", "08:00"),
    "noon":    ("Noon",    "الظهر",  "13:00"),
    "evening": ("Evening", "المساء", "19:00"),
    "bedtime": ("Bedtime", "قبل النوم", "22:00"),
}

# Units: key -> English word, Arabic (one), Arabic (few: 2 to 10)
UNITS = {
    "tablet":  ("tablet",  "قرص",   "أقراص"),
    "capsule": ("capsule", "كبسولة", "كبسولات"),
    "ml":      ("ml",      "مل",    "مل"),
    "puff":    ("puff",    "بخة",   "بخات"),
    "drop":    ("drop",    "نقطة",  "نقط"),
    "unit":    ("unit",    "وحدة",  "وحدات"),
}

# Instructions: key -> (English, Arabic)
INSTRUCTIONS = {
    "with_food":        ("With food", "مع الأكل"),
    "after_food":       ("After food", "بعد الأكل"),
    "before_food":      ("Before food", "قبل الأكل"),
    "before_breakfast": ("Before breakfast", "قبل الفطار"),
    "empty_stomach":    ("On an empty stomach", "على معدة خالية"),
    "at_bedtime":       ("At bedtime", "قبل النوم"),
    "with_water":       ("With a glass of water", "مع كوب ماء"),
}

# ---------- Helper functions ----------

def read_amount(text, row_number):
    """Turn '1', '0.5' or '1/2' into a number. Empty text means 'not taken'."""
    text = text.strip()
    if text == "":
        return 0
    try:
        if "/" in text:
            top, bottom = text.split("/")
            return float(top) / float(bottom)
        return float(text)
    except ValueError:
        sys.exit(f"Row {row_number}: '{text}' is not a number.")


def number_text(n):
    if n == 0.5:
        return "½"
    return str(int(n)) if n == int(n) else str(n)


def dose_in_english(count, unit):
    word = UNITS[unit][0]
    if unit == "ml" or count <= 1:
        return f"{number_text(count)} {word}"
    return f"{number_text(count)} {word}s"


def dose_in_arabic(count, unit):
    one, few = UNITS[unit][1], UNITS[unit][2]
    if count == 0.5:
        return f"نصف {one}"
    if 2 <= count <= 10 and count == int(count):
        return f"{number_text(count)} {few}"
    return f"{number_text(count)} {one}"


def read_medicines(path):
    medicines = []
    with open(path, newline="", encoding="utf-8") as f:
        for number, row in enumerate(csv.DictReader(f), start=2):
            name = row["drug"].strip()
            unit = row["unit"].strip().lower()
            if not name:
                sys.exit(f"Row {number}: the drug name is empty.")
            if unit not in UNITS:
                sys.exit(f"Row {number}: unit '{unit}' is not known. Use one of: {', '.join(UNITS)}")

            times = {}
            for slot in SLOTS:
                count = read_amount(row[slot], number)
                if count > 0:
                    times[slot] = count
            if not times:
                sys.exit(f"Row {number}: {name} has no time of day.")

            keys = [k.strip() for k in row["instructions"].split(";") if k.strip()]
            for k in keys:
                if k not in INSTRUCTIONS:
                    sys.exit(f"Row {number}: instruction '{k}' is not known. Use: {', '.join(INSTRUCTIONS)}")

            medicines.append({
                "name": name, "unit": unit, "times": times,
                "instructions": keys,
                "days": row["days"].strip(),
                "notes": row["notes"].strip(),
            })
    return medicines


ARABIC_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")


def ar_digits(text):
    """Show numbers inside Arabic text with Arabic-Indic digits (٠١٢٣...)."""
    return text.translate(ARABIC_DIGITS)


def esc(text):
    return html.escape(text, quote=True)


# ---------- Build the page ----------

def build_page(medicines, patient, pharmacist):
    # Table 1: list of medicines
    rows = ""
    for i, m in enumerate(medicines, start=1):
        instr_en = " / ".join(INSTRUCTIONS[k][0] for k in m["instructions"])
        instr_ar = " / ".join(INSTRUCTIONS[k][1] for k in m["instructions"])
        if m["days"]:
            time_en, time_ar = f"{m['days']} days", ar_digits(f"{m['days']} يوم")
        else:
            time_en, time_ar = "Ongoing", "مستمر"
        notes = f"<br><i>{esc(m['notes'])}</i>" if m["notes"] else ""
        rows += (
            f"<tr><td>{i}</td>"
            f"<td><b>{esc(m['name'])}</b>{notes}</td>"
            f"<td><div dir='ltr'>{esc(instr_en) or '-'}</div><div dir='rtl'>{esc(instr_ar)}</div></td>"
            f"<td><div dir='ltr'>{time_en}</div><div dir='rtl'>{time_ar}</div></td></tr>"
        )

    # Table 2: what to take at each time of day
    timeline = ""
    for slot, (en, ar, clock) in SLOTS.items():
        items = ""
        for m in medicines:
            if slot in m["times"]:
                count = m["times"][slot]
                items += (
                    f"<div class='item'><div dir='ltr'>&#9744; <b>{esc(m['name'])}</b> - "
                    f"{dose_in_english(count, m['unit'])}</div>"
                    f"<div dir='rtl'>{ar_digits(dose_in_arabic(count, m['unit']))}</div></div>"
                )
        if items:
            timeline += (
                f"<tr><td class='time'><div dir='ltr'><b>{en}</b> - {clock}</div>"
                f"<div dir='rtl'>{ar}</div></td><td>{items}</td></tr>"
            )

    today = date.today().strftime("%d/%m/%Y")
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Medication Schedule</title>
<style>
  @page {{ size: A4; margin: 14mm; }}
  body {{ font-family: Tahoma, 'Segoe UI', 'DejaVu Sans', Arial, sans-serif; font-size: 12px; color: #222; }}
  h1 {{ color: #0F4C5C; margin: 0; font-size: 22px; }}
  h2 {{ color: #0F4C5C; font-size: 15px; margin: 16px 0 4px; border-bottom: 2px solid #2A9D8F; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th {{ background: #0F4C5C; color: white; padding: 6px; text-align: left; }}
  td {{ border: 1px solid #bbb; padding: 6px; vertical-align: top; }}
  td.time {{ width: 22%; background: #EAF4F3; text-align: center; }}
  .item {{ margin-bottom: 6px; }}
  [dir='rtl'] {{ text-align: right; }}
  .info td {{ border: none; padding: 2px 0; font-size: 13px; }}
  .note {{ margin-top: 14px; padding: 8px; background: #FFF6E0; border: 1px solid #E0B94A; }}
</style></head><body>
<h1>Medication Schedule &nbsp;|&nbsp; <span dir="rtl">جدول الأدوية</span></h1>
<table class="info">
<tr><td><b>Patient / المريض:</b> {esc(patient)}</td><td><b>Date / التاريخ:</b> {today}</td></tr>
<tr><td><b>Pharmacist / الصيدلي:</b> {esc(pharmacist) or "____________________"}</td><td></td></tr>
</table>

<h2>1. My medicines &nbsp;|&nbsp; <span dir="rtl">أدويتي</span></h2>
<table border="1" cellspacing="0" cellpadding="6" width="100%">
<tr><th>#</th><th>Medicine / الدواء</th><th>How to take / طريقة الاستعمال</th><th>For how long / المدة</th></tr>
{rows}
</table>

<h2>2. My day &nbsp;|&nbsp; <span dir="rtl">يومي</span> &nbsp; (tick the box when taken / ضع علامة عند أخذ الدواء)</h2>
<table border="1" cellspacing="0" cellpadding="6" width="100%">
<tr><th>Time / الوقت</th><th>Medicines and dose / الأدوية والجرعة</th></tr>
{timeline}
</table>

<div class="note" dir="ltr">
<b>Important:</b> This schedule only copies the instructions of your doctor or pharmacist.
Do not change or stop any medicine without asking them first.
Ask your pharmacist if you miss a dose or feel unwell.
<div dir="rtl">مهم: هذا الجدول يوضّح فقط تعليمات الطبيب أو الصيدلي.
لا تغيّر أو توقف أي دواء قبل استشارتهما. اسأل الصيدلي إذا نسيت جرعة أو شعرت بتعب.</div>
</div>
</body></html>"""


def main():
    parser = argparse.ArgumentParser(description="Make a printable medication schedule.")
    parser.add_argument("csv_file", help="CSV file with the medicines")
    parser.add_argument("--patient", default="____________________")
    parser.add_argument("--pharmacist", default="")
    parser.add_argument("--out", default="schedule.html")
    args = parser.parse_args()

    medicines = read_medicines(args.csv_file)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(build_page(medicines, args.patient, args.pharmacist))
    print(f"Done: {len(medicines)} medicines. Open {args.out} and print it.")


if __name__ == "__main__":
    main()
