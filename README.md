
Inventory App v3 - Production-ready (light theme default)
---------------------------------------------------------
Files:
- mainwindow.ui     : Qt Designer UI (RTL)
- style_light.qss   : Light theme stylesheet
- style_dark.qss    : Dark theme stylesheet (switchable in settings)
- database.py       : SQLite helpers & schema
- app.py            : Main application (loads UI, dialogs, charts, CRUD)
- icons/            : SVG icons
- config.json       : Saved user settings (theme, font size)

Run:
1. python -m venv venv
2. source venv/bin/activate    (or venv\\Scripts\\activate on Windows)
3. pip install --upgrade pip
4. pip install PySide6
   (optional for charts) pip install PySide6-QtCharts
5. python app.py

Notes:
- If QtCharts not available, the Reports page will show a message but still work.
- All text and layout are RTL for Arabic.
