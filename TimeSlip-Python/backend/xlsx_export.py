# -*- coding: utf-8 -*-
"""Minimal .xlsx writer using only the standard library."""
from __future__ import print_function

import datetime
import io
import zipfile
from xml.sax.saxutils import escape


def _col_letter(n):
    name = ""
    while n:
        n, rem = divmod(n - 1, 26)
        name = chr(65 + rem) + name
    return name


def _cell(ref, value, style=0):
    if value is None or value == "":
        return '<c r="%s" s="%s"/>' % (ref, style)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return '<c r="%s" s="%s" t="n"><v>%s</v></c>' % (ref, style, value)
    text = escape(str(value))
    return '<c r="%s" s="%s" t="inlineStr"><is><t>%s</t></is></c>' % (ref, style, text)


def _sheet_xml(headers, rows):
    out = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
        "<sheetData>",
    ]
    header_row = []
    for i, h in enumerate(headers, 1):
        header_row.append(_cell(_col_letter(i) + "1", h, 1))
    out.append('<row r="1">%s</row>' % "".join(header_row))
    for r_idx, row in enumerate(rows, 2):
        cells = []
        for c_idx, value in enumerate(row, 1):
            style = 2 if r_idx == len(rows) + 1 and str(row[1]).upper() == "TOTAL" else 0
            cells.append(_cell(_col_letter(c_idx) + str(r_idx), value, style))
        out.append('<row r="%s">%s</row>' % (r_idx, "".join(cells)))
    out.append("</sheetData></worksheet>")
    return "".join(out)


def _styles_xml():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="3">
    <font><sz val="11"/><name val="Arial"/></font>
    <font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Arial"/></font>
    <font><b/><sz val="11"/><name val="Arial"/></font>
  </fonts>
  <fills count="3">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF12141A"/></patternFill></fill>
  </fills>
  <borders count="1"><border/></borders>
  <cellStyleXfs count="1"><xf/></cellStyleXfs>
  <cellXfs count="3">
    <xf xfId="0"/>
    <xf xfId="0" fontId="1" fillId="2" applyFont="1" applyFill="1"/>
    <xf xfId="0" fontId="2" applyFont="1"/>
  </cellXfs>
</styleSheet>
"""


def _workbook_xml(sheet_names):
    sheets = []
    for i, name in enumerate(sheet_names, 1):
        sheets.append('<sheet name="%s" sheetId="%s" r:id="rId%s"/>' % (escape(name), i, i))
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        "<sheets>%s</sheets></workbook>"
    ) % "".join(sheets)


def _rels_xml(count):
    parts = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
    ]
    for i in range(1, count + 1):
        parts.append(
            '<Relationship Id="rId%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet%s.xml"/>'
            % (i, i)
        )
    parts.append(
        '<Relationship Id="rId%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        % (count + 1)
    )
    parts.append("</Relationships>")
    return "".join(parts)


def _root_rels():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>
"""


def _ctype():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
</Types>
"""


def build_xlsx(headers, session_rows, summary_rows):
    buf = io.BytesIO()
    zf = zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED)
    zf.writestr("[Content_Types].xml", _ctype())
    zf.writestr("_rels/.rels", _root_rels())
    zf.writestr("xl/workbook.xml", _workbook_xml(["Sessions", "Summary"]))
    zf.writestr("xl/_rels/workbook.xml.rels", _rels_xml(2))
    zf.writestr("xl/styles.xml", _styles_xml())
    zf.writestr("xl/worksheets/sheet1.xml", _sheet_xml(headers, session_rows))
    zf.writestr(
        "xl/worksheets/sheet2.xml",
        _sheet_xml(["Field", "Value"], summary_rows),
    )
    zf.close()
    return buf.getvalue()


def format_clock(ms):
    total = max(0, int(ms) // 1000)
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    return "%02d:%02d:%02d" % (h, m, s)


def hours_decimal(ms):
    return round(float(ms) / 3600000.0, 4)


def sessions_to_xlsx(sessions, rate=0.0):
    headers = [
        "#",
        "Work comment",
        "Date",
        "Start time",
        "End time",
        "Duration (h:mm:ss)",
        "Hours to bill",
        "Hourly rate",
        "Amount to bill",
    ]
    rows = []
    total_hours = 0.0
    for i, s in enumerate(sessions, 1):
        hrs = hours_decimal(s["durationMs"])
        total_hours += hrs
        start = datetime.datetime.fromtimestamp(s["startMs"] / 1000.0)
        end = datetime.datetime.fromtimestamp(s["endMs"] / 1000.0)
        amount = round(hrs * rate, 2) if rate else ""
        rows.append(
            [
                i,
                s.get("comment") or "",
                start.strftime("%Y-%m-%d"),
                start.strftime("%Y-%m-%d %H:%M"),
                end.strftime("%Y-%m-%d %H:%M"),
                format_clock(s["durationMs"]),
                hrs,
                rate if rate else "",
                amount,
            ]
        )
    total_amt = round(total_hours * rate, 2) if rate else ""
    rows.append(
        [
            "",
            "TOTAL",
            "",
            "",
            "",
            "",
            round(total_hours, 4),
            rate if rate else "",
            total_amt,
        ]
    )
    summary = [
        ["TimeSlip billing report", ""],
        ["Generated", datetime.datetime.now().strftime("%Y-%m-%d %H:%M")],
        ["Sessions exported", len(sessions)],
        ["Total hours to bill", round(total_hours, 4)],
        ["Hourly rate", rate if rate else "not set"],
        ["Total amount", total_amt if total_amt != "" else "not set"],
    ]
    return build_xlsx(headers, rows, summary)
