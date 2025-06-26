# How to Use AI - Demo (All in English)

## 1. Setup

> 🎯 Goal: Let students run ChatGPT-generated Python code locally.

### Install VS Code

* Download: [https://code.visualstudio.com/](https://code.visualstudio.com/)
* Install the Python extension
* Open Terminal (Windows: Ctrl+`, Mac: Cmd+`)

### Install Python

* Download: [https://www.python.org/downloads/](https://www.python.org/downloads/)

* Make sure to check "Add Python to PATH"

* Verify installation:

  ```bash
  python --version
  ```

### Run Your First Python Program

1. Open VS Code, create a new file `hello.py`

2. Enter:

   ```python
   print("Hello, world!")
   ```

3. In terminal:

   ```bash
   python hello.py
   ```

4. You should see: `Hello, world!`

## 2. Project Overview

🛠️ This project demonstrates how to use **ChatGPT** to build and assemble code for a desktop "Expense Tracker" with:

- expense/income recording  
- budget reminders  
- report generation & export  
- data visualization  
- GUI  

You’ll learn:

- How to design effective prompts to generate backend logic  
  如何设计高效的 Prompt 来生成后端业务逻辑  
- How to interpret and test GPT outputs through a CLI  
  如何通过命令行测试并验证 GPT 输出的代码  
- How to integrate **pandas** and **matplotlib** for data analysis & visualization  
  如何使用 pandas 与 matplotlib 进行数据分析与可视化  
- How to connect Python backend with a **PyQt5** GUI  
  如何将 Python 后端逻辑与 PyQt5 图形界面结合  
- How to iterate and debug collaboratively with AI  
  如何与 AI 协作，快速迭代与调试代码  

## 3. Specific design

#### ① Frame construction

A solid directory scaffold makes all future development smoother. The core job now is to ask the AI to turn that into a folder/file skeleton.  

But how to ask efficiently? 

**❌Bad Prompt**

> Generate a project directory structure for a smart expense tool with features: recording, reminders, reports, visualization, GUI.

Issues:

- No tech stack or language → AI might pick JavaScript, Java, etc.
- No concrete file/folder names → unpredictable output.
- No format specification → AI may return plain text, bullet list, or paragraph.

So we should identify prompt elements first.

1. **Context/Tech Stack** - Python, SQLite, pandas, matplotlib, etc.  
2. **Requirements** - List of files/folders that implement each feature  
3. **Output Format** - Markdown fenced code block, tree-view

##### ✅ Good Prompt

> I’m building a “Expense Tracker” app using Python, SQLite, pandas, matplotlib, ect.
> It needs to support:
>
>     1. expense/income recording
>     2. budget reminders
>     3. report generation & export
>     4. data visualization
>     5. GUI
>
> Please propose an initial project directory structure:
>
>   - Include clear Python file and folder names
>   - Provide a one-line description for each item
>   - Output it as a Markdown fenced code block in a tree-view format

**Outcome**

```markdown
expense_tracker/
├── main.py                    # App entry point (launches GUI)
├── database.py               # All database operations (models + queries)
├── config.py                 # Constants (DB path, budget limits, etc.)
│
├── core/                     # Core functionality
│   ├── tracker.py           # CRUD for income/expense records
│   ├── budget.py            # Budget calculations & alerts
│   └── reports.py           # Report/visualization generation
│
├── gui/                      # User interface
│   ├── main_window.py       # Main window layout (Tkinter/PyQt)
│   └── components.py        # Reusable UI widgets (tables, charts, etc.)
│
└── data/
    ├── expenses.db          # SQLite database file
    └── exports/             # Generated reports/charts
```

Build the project according to the framework and personalize it appropriately.

![Untitled](C:\Users\SUNCHAOYI\Desktop\Untitled.png)
