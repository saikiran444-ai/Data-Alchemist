import io
import contextlib
import matplotlib.pyplot as plt
import pandas as pd
import re

def run_generated_code(datasets: dict, code: str):
    """Safely executes Gemini-generated analysis code and returns (output, figure)."""

    # ✅ Safe sandbox for controlled execution
    sandbox = {"datasets": datasets, "pd": pd, "plt": plt}
    output_buffer = io.StringIO()
    plt.close("all")

    # 🧹 Clean markdown fences & disable plt.show() (we handle it in Streamlit)
    code = code.replace("```python", "").replace("```", "").strip()
    code = re.sub(r"\bplt\.show\(\)", "# plt.show() disabled", code)

    # 🩹 Auto-fix unsupported Matplotlib args (prevents future padding/labelpad/pad errors)
    code = re.sub(r",\s*(padding|labelpad|pad)\s*=\s*\d+", "", code)

    # 🚫 Block unsafe operations
    unsafe = ["os.", "sys.", "subprocess", "open(", "shutil", "requests", "eval", "exec("]
    if any(u in code for u in unsafe):
        return "⚠️ Unsafe code blocked.", None

    try:
        with contextlib.redirect_stdout(output_buffer):
            exec(code, sandbox)

        # 🧾 Capture printed output
        output_text = output_buffer.getvalue().strip() or "✅ Code executed successfully."

        # 🖼️ Capture Matplotlib figure(s)
        figs = [plt.figure(num) for num in plt.get_fignums()]
        fig = figs[-1] if figs else None

        # 🧩 If Gemini defined a RESULT dict, extract summary safely
        RESULT = sandbox.get("RESULT")
        if RESULT and isinstance(RESULT, dict):
            summary = RESULT.get("summary", "").strip()
            output_text = f"✅ Summary: {summary}"

        return output_text, fig

    except Exception as e:
        return f"⚠️ Execution error: {e}", None