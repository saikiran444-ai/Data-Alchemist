# **Data alchemist-- AI-based e-commerce insights platform.**

The raw e-commerce data can be converted into actionable business insights with an **agentic AI analyst** developed with **Gemini, Streamlit, and Python**.  
It is a place that allows you to have a conversation with an AI, write code that builds analytics dynamically, and visualize it in real-time, with zero manual effort on exploring the Brazilian Olist dataset.

# **Features**
**Natural Language Data Analysis** -- ask everything, receive ideas immediately.  
**AI Code Generation** — Gemini generates Pandas/Matplotlib/Plotly code.  
**Automatic Code Execution** -- safe sandboxed executable.  
**Smart KPI Dashboard** - orders, customers, revenue, reviews.  
**Stunning UI 1000** -- neon mouse recoil, animated gradient title, dark theme.  
**Interactive Visualizations** — bar charts, pie charts, hybrid charts.  
**Chat Memory** — re-run old analyses Chat Memory.  
**Fully Agentic Workflow** - generate - explain - reason - execute.  

---
# **Project Structure**
maersk-ai/
│
├── app.py                       # Main Streamlit UI
├── api_server.py                # Gemini backend server
├── check.py                     # Debug tool (optional)
├── test_app.py                  # Test file (optional)
├── chat_history.json            # Stored chat sessions
│
├── data/                        # Olist dataset (.csv files)
│   ├── olist_orders_dataset.csv
│   ├── olist_order_payments_dataset.csv
│   ├── olist_customers_dataset.csv
│   └── …
│
├── utils/
│   ├── gemini_api.py            # Gemini API wrapper
│   ├── code_executor.py         # Executes generated code
│   └── chat_memory.py           # Saves/loads chat memory
│
└── logs/                        # Logs folder

## How to Run the App

###  Clone the Repository
```bash
git clone https://github.com/saikiran444-ai/maersk-ai.git
cd maersk-ai

python3 -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows

pip install -r requirements.txt
GEMINI_API_KEY=your_key_here
#Start Backend Server
python api_server.py
#Run
streamlit run app.py


Technologies Used
	•	Python 3.10+
	•	Streamlit
	•	Google Gemini API
	•	Pandas
	•	Matplotlib
	•	Plotly
	•	HTML/CSS/JS
	•	JSON Storage

Future Improvements -
	*	 Autonomous multi-step planning (true agent)
	*	 Auto-dashboard generation from a single prompt
	*	 User authentication
	*	 Real-time APIs instead of static CSV data
