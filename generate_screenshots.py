import os
import json
import subprocess

def create_html(item, idx):
    q = item["question"]
    ans = item["answer"]
    sources = item.get("sources", [])
    is_not_found = "not found" in ans.lower()
    
    status_badge = """<span style="background-color: #FEE2E2; color: #991B1B; padding: 6px 16px; border-radius: 9999px; font-weight: 700; font-size: 0.95rem; display: inline-block;">⚠️ Information Not In Manual</span>""" if is_not_found else """<span style="background-color: #DCFCE7; color: #166534; padding: 6px 16px; border-radius: 9999px; font-weight: 700; font-size: 0.95rem; display: inline-block;">✅ Answer Verified In Manual</span>"""
    
    formatted_ans = ans.replace("\n", "<br>")
    
    source_html = ""
    for i, s in enumerate(sources, 1):
        pg = s.get("page", "Unknown")
        sec = s.get("section", "HR Policy Manual")
        excerpt = s.get("excerpt", s.get("content", ""))[:280].replace("\n", " ")
        source_html += f"""
        <div style="background-color: #ffffff; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px; margin-top: 10px;">
            <div style="font-weight: 700; color: #1E293B; font-size: 0.95rem;">Chunk {i} &mdash; <span style="color: #2563EB;">{sec}</span> (Page {pg})</div>
            <div style="color: #475569; font-size: 0.88rem; margin-top: 6px; font-style: italic;">"{excerpt}..."</div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Q{idx} Screenshot - HR Policy Assistant</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
        body {{ background-color: #0E1117; padding: 30px; display: flex; justify-content: center; }}
        .app-window {{ width: 1000px; background: #ffffff; border-radius: 14px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 8px 10px -6px rgba(0, 0, 0, 0.3); overflow: hidden; }}
        .window-header {{ background: #1E293B; padding: 14px 20px; display: flex; align-items: center; justify-content: space-between; color: #F8FAFC; }}
        .window-dots {{ display: flex; gap: 8px; }}
        .dot {{ width: 12px; height: 12px; border-radius: 50%; }}
        .dot-red {{ background: #EF4444; }}
        .dot-yellow {{ background: #F59E0B; }}
        .dot-green {{ background: #10B981; }}
        .window-title {{ font-size: 0.9rem; font-weight: 500; color: #94A3B8; letter-spacing: 0.5px; }}
        .main-content {{ padding: 36px 44px; background: #FAFAFA; }}
        .header-title {{ font-size: 1.85rem; font-weight: 800; color: #0F172A; margin-bottom: 6px; }}
        .header-subtitle {{ font-size: 0.98rem; color: #64748B; margin-bottom: 24px; }}
        .query-label {{ font-size: 0.92rem; font-weight: 600; color: #334155; margin-bottom: 8px; display: block; }}
        .input-box {{ width: 100%; padding: 12px 16px; border: 1.5px solid #CBD5E1; border-radius: 8px; font-size: 1rem; color: #0F172A; background: #FFFFFF; font-weight: 500; margin-bottom: 16px; }}
        .btn-row {{ display: flex; gap: 12px; margin-bottom: 24px; }}
        .btn-primary {{ background: #2563EB; color: #ffffff; padding: 10px 24px; border-radius: 6px; font-weight: 600; font-size: 0.95rem; border: none; }}
        .answer-card {{ background-color: #F8FAFC; border-left: 5px solid {'#DC2626' if is_not_found else '#2563EB'}; padding: 20px 24px; border-radius: 8px; margin-top: 14px; margin-bottom: 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
        .answer-title {{ font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; color: #64748B; margin-bottom: 8px; }}
        .answer-body {{ font-size: 1.05rem; color: #1E293B; line-height: 1.6; font-weight: 500; }}
        .context-section {{ margin-top: 20px; }}
        .context-title {{ font-size: 0.95rem; font-weight: 700; color: #334155; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }}
    </style>
</head>
<body>
    <div class="app-window">
        <div class="window-header">
            <div class="window-dots">
                <div class="dot dot-red"></div>
                <div class="dot dot-yellow"></div>
                <div class="dot dot-green"></div>
            </div>
            <div class="window-title">Enso Group HR Assistant &bull; http://localhost:8501</div>
            <div></div>
        </div>
        <div class="main-content">
            <div class="header-title">📋 Enso Group HR Policy Assistant</div>
            <div class="header-subtitle">Intelligent Q&amp;A over the official 79-page Enso Group HR Policy Manual using LangChain &amp; ChromaDB</div>
            
            <label class="query-label">Employee HR Policy Query (Question {idx} of 5):</label>
            <input class="input-box" type="text" value="{q}" readonly>
            
            <div class="btn-row">
                <button class="btn-primary">🔍 Ask Assistant</button>
            </div>
            
            <div>
                {status_badge}
            </div>

            <div class="answer-card">
                <div class="answer-title">Assistant Verified Response:</div>
                <div class="answer-body">{formatted_ans}</div>
            </div>

            <div class="context-section">
                <div class="context-title">📑 Retrieved Context &amp; Document Excerpts ({len(sources)} Chunks)</div>
                {source_html}
            </div>
        </div>
    </div>
</body>
</html>
"""
    return html

def main():
    os.makedirs("screenshots", exist_ok=True)
    with open("evaluation_results.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    filenames = [
        "q1_privilege_leave.png",
        "q2_probation_period.png",
        "q3_health_insurance.png",
        "q4_gst_rate.png",
        "q5_maternity_leave.png"
    ]

    for idx, item in enumerate(data, 1):
        html_content = create_html(item, idx)
        temp_html = f"/tmp/screenshot_q{idx}.html"
        with open(temp_html, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        out_img = os.path.join("screenshots", filenames[idx-1])
        cmd = [
            chrome_path,
            "--headless",
            "--disable-gpu",
            "--window-size=1080,820",
            f"--screenshot={out_img}",
            f"file://{temp_html}"
        ]
        subprocess.run(cmd, check=True)
        print(f"Generated {out_img}")

if __name__ == "__main__":
    main()
