# Django Code Audit

**Django Code Audit** is a reusable Django app that automates Python code quality checks using **Pylint**, stores audit reports in the database, and provides an **admin interface** to view both latest and historical scores.

---

## 🚀 Features

- Run **Pylint** checks on Django apps, modules, or files
- Store audit reports and pylint scores in the database
- View **latest score** and **all past runs** in Django Admin
- Generate HTML reports for detailed review
- Supports project-specific `.pylintrc` configuration
- Easy integration with existing Django projects

---

## ⚡ Installation

1. **Install the package** via pip:

```bash
pip install django-code-audit
```

2. Add the app to **INSTALLED_APPS** in your Django project’s settings.py:
````pythonpython
INSTALLED_APPS = [
    ...
    'code_audit',
    ...
]


CODE_AUDIT = {
    "DEFAULT_PYLINTRC": "/path/to/.pylintrc",
    "BASE_DIR": True,  # enable per-author level reports
}
````
3. Run **migrations** to create necessary database tables:
```bash
python manage.py migrate code_audit
``` 
## 4. Usage Instructions (via **Django Admin**)

Follow these steps to create and run a code audit report efficiently:

### **Step 1: Login**
🔑 Login to your Django Admin dashboard.

### **Step 2: Navigate to Code Audit Reports**
📂 In the admin sidebar, click on **Code Audit Reports**.

### **Step 3: Add a New Report**
➕ Click **Add Code Audit Report**.

### **Step 4: Fill Mandatory Fields**
Fill in the following fields:

- **Module Name** – The Django app or module you want to audit.  
- **File Name** – Python file or app to audit.  
- **Report Path** – Directory where the HTML report will be stored (e.g., `/tmp/`).  

> Make sure all mandatory fields are filled; otherwise, the report cannot be generated.

### **Step 5: Save the Report**
💾 Click **Save** to create the audit report entry.

### **Step 6: Run the Audit**
▶️ After saving, click **Run Report** to generate the code audit using Pylint.

### **Step 7: View the Report**
👀 Once the audit is complete, click **View Report** to open the HTML report in your browser.

### **Step 8: Check Scores**
📊 In the admin interface, you can:
- View the **latest pylint score** for this report.
- Browse **all historical scores** for each run.

## 4.File Author Level Reports
Django Code Audit supports generating per-author reports by filtering files that explicitly declare a maintainer or author inside the file itself.

Author Declaration Format

To be included in an author-specific audit, each file must contain a docstring with one of the following patterns (case-insensitive):
```python:python
"""
current maintainer: ravi
"""

or

"""
current maintainer: ravi
"""
```
The system will scan all .py files in the given app/module and include only those files where the declared author matches the File Author field specified in the report.

### Example

#### chat.py:
```python:python
"""
current maintainer: ravi
"""
def send_message():
    return "ok"
```

#### utils.py:
```python:python
"""
author: john
"""
```
If you create a Code Audit Report with:

File Author = ravi

✅ chat.py will be included in the audit.

❌ utils.py will be excluded.

> **Tip:** You can customize Pylint rules by providing a `.pylintrc` file in your project.


## ## 🛠️ Configuration
You can customize the behavior of Django Code Audit by adding the following settings to your `settings.py`:

By default, the app uses the project’s .pylintrc if available.