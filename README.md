## Automate Your Cold Emails 

This Python project streamlines your sales prospecting with a two-step solution:

* **Opener Agent:** Craft personalized cold emails for each lead in your CSV.
* **Escalator Agent:** Analyze lead responses and take the next steps (escalate or request more info).

**Get Started Quickly:**

1. **Python Version**

   - This project requires Python 3.11.1.

2. **Clone the Repository:**

   ```bash
   git clone https://github.com/Mufaddal2153/opener_escalator_chat.git
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Your LLM:**

   - Replace `llm = ...` in `main.py` with your LLM interaction library's object (e.g., ChatOpenAI).
   - Obtain your OpenAI API key (if using OpenAI) and set the appropriate environment variable.

5. **Prepare Your Leads:**

   - Create a CSV file named `leads.csv` with columns like `Name`, `Company`, etc.
   - Ensure a column named `Looking For` captures the lead's initial needs.

6. **Run the Script:**

   - Follow ipython notebook `main.ipynb` for running the script.

   The script generates personalized emails for each lead and stores them along with relevant data in a new CSV files (`opener_output.xlsx` and `escalator_output.xlsx`).

**Key Features:**

* **SOLID Principles:** Clean, maintainable codebase.
* **Customizable Templates:** Tailor email introductions for your brand.
* **LLM Integration:** Leverage powerful language models for personalization.
* **Seamless Response Handling:** Automate next steps based on lead replies.

**Additional Notes:**

* Ensure you have Python installed (version specified in `README.md`).
* Refer to the code for specific LLM library configuration details.
* Feel free to adjust parameters and the flow in `main.py`.