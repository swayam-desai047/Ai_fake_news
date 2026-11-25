# MIT-WPU Mini Project Report: College Format Specification (from the 4 supplied .docx templates)

Source key used in citations below (all are local files, inspected at XML level: word/document.xml, styles.xml, settings.xml, rels, media; rendered with LibreOffice):
- [FMT] = `/root/.claude/uploads/1906c76c-bbe3-5864-8def-44e8386987c9/67b0a3c5-Mini_Project_Report_Format.docx`
- [TITLE] = `/root/.claude/uploads/1906c76c-bbe3-5864-8def-44e8386987c9/d10190ee-Title_Page-1.docx`
- [CERT] = `/root/.claude/uploads/1906c76c-bbe3-5864-8def-44e8386987c9/53d63902-Certificate.docx`
- [ACK] = `/root/.claude/uploads/1906c76c-bbe3-5864-8def-44e8386987c9/a5547acd-Acknowledgement_Page.docx`

Unit conversions used: 1440 twips = 1 in = 2.54 cm; 914400 EMU = 1 in; Word `sz` is in half-points; `spacing line` with lineRule=auto is in 240ths of a line (240 = single, 360 = 1.5); `before/after` are twips (20 twips = 1 pt).

Assets extracted (reusable):
- `/home/user/Ai_fake_news/research_notes/News aggregator report audit/assets/mitwpu_logo_wide_1081x177.png` (from [FMT], [TITLE], [CERT]; all three are byte-identical, md5 6825294e4c58e33b3667d2d6beecf69a; 1081x177 px RGBA, 96 dpi; "Dr. Vishwanath Karad MIT WORLD PEACE UNIVERSITY | PUNE / TECHNOLOGY, RESEARCH, SOCIAL INNOVATION & PARTNERSHIPS" lockup with MIT-WPU dome)
- `/home/user/Ai_fake_news/research_notes/News aggregator report audit/assets/mitwpu_logo_ack_500x144.png` (from [ACK]; md5 3d43bc8de009298a6ee662d7aee738ce; 500x144 px RGBA, 96 dpi; same lockup, more compact proportions; docPr name "image4.png", descr "MIT-WPU-logo")
- Reference renders: `.../assets/render_fmt.pdf`, `render_title.pdf`, `render_cert.pdf`, `render_ack.pdf`, `render_all_pages.png` (LibreOffice render; NOTE: Times New Roman and Algerian are NOT installed in this container, so renders use substitute fonts; layout is indicative only).

---

## 1. Full text of the Mini Project Report Format document (verbatim) and prescribed structure

### Takeaway
The "Mini Project Report Format" file contains NO written guidelines at all: its entire content is the MIT-WPU logo, the heading "Index", and a 3-column index table listing 11 chapters and their numbered sub-sections. Everything else (fonts for body text, numbering rules, captions, binding, copies) is unspecified by the college files.

### Cited Findings
- Complete body of [FMT], in order: (1) a paragraph holding the anchored logo followed by three tab characters; (2) an empty centred paragraph; (3) centred paragraph "Index" (Times New Roman, bold, 18 pt / sz 36); (4) the index table; (5) the closing section properties. There is no other text, no guidelines list, no list of figures/tables, no sequence-of-pages statement — [FMT] word/document.xml
- Index table, verbatim (header row is "Sr. No. | Contents | Page No."; the Page No. column is empty in every row) — [FMT] word/document.xml:

| Sr. No. | Contents | Page No. |
|---|---|---|
| **1** | **Introduction** | |
| 1.1 | Existing System | |
| 1.2 | Need for System | |
| 1.3 | Scope of System | |
| 1.4 | Operating Environment - Hardware and Software | |
| 1.5 | Brief Description of Technology Used | |
| **2** | **Proposed System** | |
| 2.1 | Feasibility Study | |
| 2.2 | Objectives of Proposed System | |
| 2.3 | Users of System | |
| **3** | **Analysis and Design** | |
| 3.1 | System Requirements (Functional and Non-Functional requirements) | |
| 3.2 | Module Hierarchy Diagram | |
| 3.3 | Architecture Diagram | |
| 3.4 | Class Diagram | |
| 3.5 | Use-case Diagram | |
| 3.6 | Sequence Diagram | |
| 3.7 | Activity Diagram | |
| 3.8 | Component Diagram | |
| 3.9 | Deployment Diagram | |
| 3.10 | Sample Input and Output Screens | |
| **4** | **Coding** | |
| 4.1 | Code snippets | |
| **5** | **Testing Process** | |
| 5.1 | Test Planning | |
| 5.2 | Software Testing Life Cycle (STLC) | |
| 5.3 | Types of Testing | |
| 5.4 | Sample Test Cases | |
| **6** | **Reports** | |
| **7** | **Summary/Conclusion/Interpretation** | |
| **8** | **Limitations of  System** (sic, two spaces) | |
| **9** | **Proposed Enhancements / Future Scope** | |
| **10** | **Key Learnings from Project** | |
| **11** | **Bibliography** | |

- Exact stored strings with trailing spaces: "Brief Description of Technology Used " and "Sample Input and Output Screens " have a trailing space; "Limitations of  System" has a double space — [FMT] word/document.xml
- Diagrams prescribed (as sub-sections of Chapter 3): Module Hierarchy, Architecture, Class, Use-case, Sequence, Activity, Component, Deployment, plus Sample Input and Output Screens. Object diagram, DFD and ER diagram are NOT listed — [FMT] word/document.xml
- Index table formatting: style "TableGrid" (single 4/8 pt black borders all round and inside), width auto, column grid 1951 / 5528 / 1560 twips = 3.44 / 9.75 / 2.75 cm (1.355 / 3.839 / 1.083 in); all text Times New Roman. Header row: bold 12 pt, centred. Chapter rows (1–11): bold 14 pt, number centred, title left-aligned. Sub-section rows (x.y): regular 14 pt, number centred, title left. Page No. cells are centred and empty. Table-cell paragraphs have spacing after 0, single line (TableGrid style) — [FMT] word/document.xml, styles.xml
- The logo in [FMT] is a floating anchor: extent 4482733 x 809244 EMU = 4.902 x 0.885 in = 12.45 x 2.25 cm, horizontal offset 754380 EMU (2.10 cm / 0.825 in) from the left margin, vertical offset 741680 EMU (2.06 cm / 0.811 in) below its paragraph, wrap Top-and-Bottom — [FMT] word/document.xml
- docProps reports Pages = 2 (the index table runs onto a second page, rows 5.3 onward in the render) — [FMT] docProps/app.xml; render_fmt.pdf

### Inferences
- The only prescribed "sequence of pages" is implied by the four files supplied: Title Page → Certificate (one per student) → Acknowledgement → Index → Chapters 1–11 (Bibliography is chapter 11, inside the index). This order is inferred, not stated.
- Because Chapters 6–11 have no sub-sections, they should be single headings in the TOC with no x.y entries.
- Chapter titles should be reproduced exactly as in the table (e.g. "Use-case Diagram", "Code snippets" lowercase s, "Summary/Conclusion/Interpretation" without spaces around slashes); a generator may trim the trailing spaces and collapse the double space in "Limitations of  System" as these look like typing artefacts (flag to user).

### Gaps
- No guidelines text exists for: body font/size, heading styles, line spacing for chapter text, page numbering, figure/table captions, bibliography style, binding, number of copies, declaration, abstract, list of figures/tables/abbreviations. None of these can be specified from the college files.

---

## 2. Page setup in each file

### Takeaway
Title, Certificate and Acknowledgement are A4 portrait with 1-inch (2.54 cm) margins on all four sides; the Format/Index file is US Letter with the same margins. Header/footer distance 708 twips (1.25 cm) everywhere; gutter 0; single section; one column.

### Cited Findings
- [TITLE], [CERT], [ACK]: `pgSz w=11906 h=16838` twips = 21.00 x 29.70 cm = 8.27 x 11.69 in (A4), portrait (no orient attribute) — sectPr in each word/document.xml
- [FMT]: `pgSz w=12240 h=15840` = 8.5 x 11 in = 21.59 x 27.94 cm (US Letter), portrait — [FMT] sectPr
- All four: `pgMar top=1440 right=1440 bottom=1440 left=1440` = 2.54 cm / 1.00 in each; `header=708 footer=708` = 1.249 cm / 0.492 in; `gutter=0`; `cols space=708`; `docGrid linePitch=360`; default tab stop 720 twips (1.27 cm / 0.5 in); compatibilityMode 15 (Word 2013+); no mirrorMargins, no evenAndOddHeaders — sectPr + settings.xml of each file
- No headerReference/footerReference, no header*.xml/footer*.xml parts, no pgNumType, no PAGE fields, no pgBorders in any of the four files — package listing + document.xml of each

### Inferences
- Use A4 portrait, 2.54 cm margins all round, header/footer 1.25 cm, gutter 0 for the whole report (the Letter size in [FMT] is most likely an authoring default, since the three page templates are A4).

### Gaps
- No binding margin/gutter is prescribed (gutter = 0).

---

## 3. Fonts, sizes, spacing, alignment

### Takeaway
Every visible template text uses Times New Roman (explicit run fonts or the "Default"/Normal styles), except the word "Certificate" which is Algerian 32 pt underlined. Sizes used: 22 pt (school name), 20 pt (project title), 18 pt ("Index"), 16 pt (title-page lines), 14 pt (index entries, ACK heading), 13 pt (certificate body), 12 pt (ACK body, cert signatures, index header). No body-chapter heading or caption styles are defined.

### Cited Findings
- [TITLE]/[CERT] style "Default": Times New Roman, 12 pt, colour 000000, spacing after 0, line 240 auto (single) — styles.xml
- [TITLE]/[CERT] docDefaults: theme minor font (Calibri) 11 pt; paragraph spacing after 160 twips (8 pt), line 259 auto (1.08); Normal style has no overrides. So empty "Normal" paragraphs on those pages are Calibri 11 pt, 8 pt after, 1.08 lines — styles.xml
- [FMT] docDefaults: Calibri 11 pt, spacing after 200 (10 pt), line 276 auto (1.15); so the "Index" heading paragraph has 10 pt after, 1.15 lines — [FMT] styles.xml
- [ACK] Normal: Times New Roman 11 pt, spacing after 0, single (line 240), widowControl off; "Body Text" style = Normal + 12 pt — [ACK] styles.xml
- Certificate body: TNR 13 pt (sz 26), justified (jc=both), line 360 auto = 1.5 lines, spacing after 8 pt (inherited default) — [CERT] document.xml
- Acknowledgement body: Body Text 12 pt TNR, justified, line 360 auto = 1.5 lines; first paragraph space before 90 twips (4.5 pt), second 202 twips (10.1 pt); left indent 220 twips (0.39 cm / 0.153 in), right indent 598 twips (1.05 cm) and 588 twips (1.04 cm) respectively; no first-line indent — [ACK] document.xml
- No first-line indents anywhere; no italic anywhere; no all-caps formatting (ACK heading is typed in capitals) — all four document.xml

### Inferences
- For a generator: use Times New Roman throughout; justify body text with 1.5 line spacing (both narrative templates, CERT and ACK, use jc=both + line 360). Chapter/section heading sizes can mirror the index (14 pt bold chapters, 14 pt regular sections) but this is inference, not prescription.

### Gaps
- No prescribed sizes/styles for chapter headings, section headings, sub-headings, captions or table text inside chapters.

---

## 4. Page numbering, header/footer, borders

### Takeaway
None of the four files contains page numbers, headers, footers or page borders. The only hint is the empty "Page No." column in the index.

### Cited Findings
- No header/footer parts, no PAGE fields, no pgNumType (so no roman/arabic scheme), no pgBorders — package listings and document.xml of all four files
- Index table has a "Page No." column, left blank — [FMT] document.xml

### Inferences
- Page numbers are needed to fill the Index; the format (roman for preliminary pages, arabic from Chapter 1, position) is the student's/generator's choice. Common practice, not a college rule: no number on title/certificate pages, arabic numbers in footer centre from Chapter 1.

### Gaps
- Numbering style, position and starting page are unspecified.

---

## 5. Figure/table numbering, captions, references, binding, copies, signatures

### Takeaway
Not specified in any supplied file, except signatures shown on the certificate (Project Guide, Program Head, Program Director) and the student name/PRN lines on the acknowledgement.

### Cited Findings
- Certificate signature block names: "Prof. Navnath Shete / Project Guide", "Dr. P. S. Metkewar / Program Head", "Dr. Anuradha Kanade / Program Director" — [CERT] document.xml
- Acknowledgement ends with "Student Name - ", "PRN - ", "Place: Pune", "Date:" — [ACK] document.xml
- Bibliography is chapter 11 in the index, no citation style given — [FMT] document.xml

### Gaps
- No figure/table numbering or caption rule; no bibliography style (IEEE/APA etc.); no binding instructions; no number of copies; no statement that each student needs their own certificate (the one-certificate-per-student requirement comes from the brief, and is consistent with the cert's single "Student Name" placeholder).

---

## 6. Title page: exact layout and text

### Takeaway
One A4 page: wide MIT-WPU logo at top-left, then centred bold lines in Times New Roman: school (22 pt), department, class/semester, year, "Mini Project Report", "On" (16 pt), red project title (20 pt), "Submitted By" + red student-name/PRN placeholder, "Under Guidance of" + two names (16 pt).

### Cited Findings (paragraph-by-paragraph, in order; "Default" = TNR 12 pt single 0 after; "Normal" = Calibri 11, 8 pt after, 1.08 line) — [TITLE] document.xml
1. Normal paragraph holding floating logo `media/image1.png` (docPr name "image1.png"): extent 4482733 x 809244 EMU = 12.45 x 2.25 cm (4.902 x 0.885 in); positionH relative to margin offset 0 (flush with left margin); positionV relative to paragraph offset 281940 EMU = 0.78 cm (0.308 in); wrapTopAndBottom; not behind text.
2. Normal, empty.
3. Default, centred, bold 22 pt: `School of Computer Science & Engineering`
4. Default, centred, empty.
5. Default, centred, bold 16 pt: `Department of Computer Science and Applications`
6–7. Default, centred, empty ×2.
8. Default, centred, bold 16 pt: `FYMScCS Sem - II` (stored as runs "F","Y","M","ScCS ","Sem - II"; hyphen-minus)
9. Default, centred, empty.
10. Default, centred, bold 16 pt: `Year - 2025-26`
11–12. Default, centred, empty ×2.
13. Default, centred, bold 16 pt: `Mini Project Report`
14–15. Default, centred, empty ×2.
16. Default, centred, bold 16 pt: `On`
17. Default, centred, empty.
18. Normal, centred, TNR bold 20 pt, colour FF0000 (red = placeholder): `“Project Title”` (curly quotes)
19. Normal, centred, empty.
20. Normal, centred, TNR bold 16 pt: `Submitted By`
21. Normal, centred, TNR bold 16 pt, red: `Student Full Name – PRN` (en dash)
22. Normal, centred, empty.
23. Normal, centred, TNR bold 16 pt: `Under Guidance of`
24. Normal, centred, TNR bold 16 pt, black: `Mr. Navnath Shete`
25. Normal, centred, TNR bold 16 pt, black: `Dr. Meenal Jabde`
- No border, no header/footer — [TITLE]

### Placeholder mapping (title page)
| Template text | Known value |
|---|---|
| “Project Title” (red) | “AI-Powered News Aggregator with Advanced Credibility and Content Analysis” (render in black once filled) |
| Student Full Name – PRN (red, one line) | four lines: Swayam Desai – 1272260064; Vinit Mistry – 1272260066; Hetvi Patel – 1272260131; Tapaswini Nayak – 1272262064 |
| FYMScCS Sem - II | class is FYMScCS (First Year M.Sc. Computer Science); semester: NO known value (template says Sem - II; certificate template says Sem – I) |
| Year - 2025-26 | Year - 2026-27 (template uses short form "2025-26"; brief gives "2026-2027") |
| Mr. Navnath Shete / Dr. Meenal Jabde | Prof. Pradeep Tiwari (mentor). Whether a second name (e.g. coordinator) belongs here is unknown |
| School / Department lines | already match the known facts |

### Inferences
- Red text marks placeholders; filled values should become black (the guide names in the sample are black).
- Course code MSC40040, Group Id 17 and "Team leader" have no slot on the title page; adding them would deviate from the template (flag to user).

### Gaps
- Semester number for this project; whether "Under Guidance of" should list one or two people; whether the university full name text is expected (it only appears inside the logo image).

---

## 7. Certificate: verbatim text, layout, signature blocks

### Takeaway
A4 page: logo top-left, school (22 pt bold) and department (16 pt bold) centred, "Certificate" in Algerian 32 pt underlined, a justified 13 pt TNR 1.5-spaced certifying paragraph with red placeholders for student name and project title, Date/Place lines, and a borderless 3-column signature table (Project Guide, Program Head, Program Director). Only the student name (and his/her, He/She pronouns) changes per student.

### Cited Findings (in order) — [CERT] document.xml, styles.xml
1. Normal paragraph with floating logo, identical image and geometry to the title page (12.45 x 2.25 cm, posH 0 from margin, posV 0.78 cm, wrapTopAndBottom).
2. Normal, empty.
3. Default, centred, bold 22 pt: `School of Computer Science & Engineering`
4. Default, centred, empty.
5. Normal, centred, TNR bold 16 pt: `Department of Computer Science and Applications`
6. Normal, centred, empty.
7. Normal, centred: `Certificate` — font Algerian (cs font TNR), 32 pt (sz 64), underline single, NOT bold for Latin text (only bCs, complex-script bold, is set).
8. Justified, line 1.5, empty.
9. Justified, line 1.5, TNR 13 pt, verbatim:
   `This is to certify that, ` **`Student Name`** (bold red) ` has successfully completed his/her mini project entitled ` **`“Mini Project title”`** (bold red, curly quotes) ` in partial fulfillment of FYMScCS Sem – I, for the year 2025-26. He/She has worked under our guidance and direction.`
   (Note: "Sem – I" uses an en dash; "fulfillment" US spelling; regular weight except placeholders.)
10. Justified 1.5, empty.
11. Justified 1.5, TNR 13 pt: `Date: `
12. Justified 1.5, TNR 13 pt: `Place:`
13–14. Justified 1.5, empty ×2.
15–16. Normal centred, empty ×2.
17. Signature table: style TableGrid but with ALL borders set to none (invisible table); width auto; grid 3159 / 2853 / 3014 twips (5.57 / 5.03 / 5.32 cm); cell widths 3369 / 3015 / 3192 twips. Cell paragraphs: centred, TNR bold 12 pt, spacing after 8 pt, line 1.08:
   - Col 1: `Prof. Navnath Shete` / `Project Guide`
   - Col 2: `Dr. P. S. Metkewar` / `Program Head` / (empty paragraph)
   - Col 3: `Dr. Anuradha Kanade` / `Program Director`
18–19. Normal, empty ×2.
- No signature lines drawn, no examiner, no Dean/HoD block, no page border, no college seal box — [CERT] document.xml

### Per-student certificate (4 copies) — what changes
| Field | Swayam Desai | Vinit Mistry | Hetvi Patel | Tapaswini Nayak |
|---|---|---|---|---|
| Student Name | Swayam Desai | Vinit Mistry | Hetvi Patel | Tapaswini Nayak |
| his/her, He/She | template keeps both; choosing one requires gender, NOT given in brief | | | |
Fixed for all four: project title, class/semester, year, signatories. No PRN slot exists on the certificate.

| Placeholder | Known value |
|---|---|
| “Mini Project title” | “AI-Powered News Aggregator with Advanced Credibility and Content Analysis” |
| FYMScCS Sem – I | semester unknown (conflicts with title page "Sem - II") |
| 2025-26 | 2026-27 |
| Prof. Navnath Shete / Project Guide | Prof. Pradeep Tiwari / Project Guide |
| Dr. P. S. Metkewar / Program Head | no new value given (keep template name unless told otherwise) |
| Dr. Anuradha Kanade / Program Director | no new value given (keep template name unless told otherwise) |
| Date / Place | not given (ACK template uses "Place: Pune") |

### Inferences
- Algerian is a Windows font; if unavailable the generator should embed/substitute carefully, as the render here fell back to a sans font.

### Gaps
- Gender/pronoun choice per student; semester; whether Program Head/Director names are current for 2026-27.

---

## 8. Acknowledgement: verbatim text and layout

### Takeaway
A4 page with the compact MIT-WPU logo inline (indented ~4.39 cm), a bold 14 pt thick-underlined "ACKNOWLEDGEMENT" heading, two justified 1.5-spaced 12 pt TNR paragraphs written in first-person singular (with leftover "internship" wording and an OCR typo "1ike"), then "Student Name - ", "PRN - ", "Place: Pune", "Date:".

### Cited Findings (in order) — [ACK] document.xml, styles.xml
1. Body Text paragraph, left indent 2490 twips (4.39 cm / 1.729 in), containing INLINE logo (not floating): extent 2847340 x 822959 EMU = 7.91 x 2.29 cm (3.114 x 0.900 in), file media/image1.png (500x144 px).
2–3. Body Text, empty ×2.
4. Normal, centred, space before 264 twips (13.2 pt), indents left 1061 (1.87 cm) right 736 (1.30 cm): `ACKNOWLEDGEMENT` — TNR bold 14 pt, underline "thick".
5–7. Body Text, empty ×3 (last has 0.25 pt before).
8. Body Text 12 pt TNR, justified, line 1.5, before 4.5 pt, indent left 0.39 cm right 1.05 cm, verbatim:
   `I wish to express my gratitude for providing the facilities of the Institute and for encouragement of this work. I would also 1ike to gratefully acknowledge the enthusiastic supervision of my internship guide Prof. ------------------------------- for his/her continuous, valuable guidance, patience, constant care and kind encouragement throughout the internship work that made me present this internship report in an efficient manner.`
   (exactly 31 hyphens after "Prof. "; "1ike" with digit one is in the source)
9. Body Text, justified, line 1.5, before 10.1 pt, indent left 0.39 cm right 1.04 cm, verbatim:
   `I would like to thank Dr. P. S. Metkewar, Program Head for providing me with guidance and help on every step of the way during this mini project and for imparting me with invaluable knowledge and teaching me the etiquettes of a professional employee.`
10–14. Body Text, empty ×5.
15. Body Text, line 535 auto (2.23 lines), indent left 220 twips, right 7097 twips (12.52 cm, i.e. a narrow left block): `Student Name - `
16. Same formatting: `PRN - `
17–19. Body Text, empty ×3.
20. Normal (TNR 11 pt): `Place: Pune`
21. Normal, empty.
22. Normal (TNR 11 pt): `Date:`

### Placeholder mapping
| Placeholder | Known value |
|---|---|
| Prof. ------------------------------- | Prof. Pradeep Tiwari |
| Student Name - | four students (see below) |
| PRN - | 1272260064 / 1272260066 / 1272260131 / 1272262064 |
| Date: | not given |

### Inferences
- The narrow right indent on the Student Name/PRN lines (12.52 cm) is meant for one name; for four members, either repeat the "Student Name - … / PRN - …" pair four times or use one acknowledgement per student. The template is singular ("I", "my", "me"), suggesting a group version would need "We/our" — a wording change the user must approve.
- "internship guide", "internship work", "internship report" are leftovers from an internship template; the user should decide whether to change to "project guide"/"mini project"; "1ike" should be corrected to "like".

### Gaps
- Whether one group acknowledgement or four individual ones is expected.

---

## 9. Other mandatory pages and order

### Takeaway
Only four page types are evidenced: Title Page, Certificate, Acknowledgement, Index (+ the 11 chapters, with Bibliography as chapter 11). No declaration, abstract, list of figures, list of tables or list of abbreviations is mentioned anywhere.

### Cited Findings
- [FMT] contains only the Index; [TITLE], [CERT], [ACK] are the only other supplied page templates — all four files.

### Inferences
- Recommended generator order: Title Page → Certificate ×4 (Swayam Desai, Vinit Mistry, Hetvi Patel, Tapaswini Nayak; team-leader first) → Acknowledgement → Index → Chapters 1–11. Adding abstract/lists of figures would be extra, not required.

### Gaps
- Known facts with NO placeholder in any template: Course code MSC40040, Group Id 17, Team leader designation (Swayam Desai), full university name as text (it appears only in the logo image).
- Placeholders with NO known value: semester (Sem I vs II conflict between templates), Date (certificate and acknowledgement), Place on certificate (ACK uses Pune), per-student pronouns, second guidance name on title page (template shows two), confirmation of Program Head (Dr. P. S. Metkewar) and Program Director (Dr. Anuradha Kanade) for 2026-27.
- Inconsistency to flag: title template says "FYMScCS Sem - II" while certificate template says "FYMScCS Sem – I"; both templates say 2025-26 while the project year is 2026-27.
