import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

# ----------------- PALETTE & CONSTANTS -----------------
BG_COLOR = RGBColor(10, 14, 23)        # #0A0E17
CARD_BG = RGBColor(17, 24, 39)         # #111827
CARD_BORDER = RGBColor(30, 41, 59)     # #1E293B
CYAN = RGBColor(2, 132, 199)           # #0284C7
CYAN_BRIGHT = RGBColor(56, 189, 248)   # #38BDF8
EMERALD = RGBColor(16, 185, 129)       # #10B981
AMBER = RGBColor(245, 158, 11)         # #F59E0B
RED = RGBColor(239, 68, 68)            # #EF4444
TEXT_PRIMARY = RGBColor(248, 250, 252) # #F8FAFC
TEXT_MUTED = RGBColor(148, 163, 184)   # #94A3B8
TEXT_DARK = RGBColor(15, 23, 42)

SCREENSHOTS_DIR = "/home/ilyan/ilmai/docs/screenshots"

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # completely blank layout

    def add_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()
        return bg

    def add_card(slide, left, top, width, height, border_color=CARD_BORDER, fill_color=CARD_BG):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = fill_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(1.5)
        else:
            card.line.fill.background()
        return card

    def add_header(slide, category, title, subhead=None):
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.7), Inches(1.1))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        # Category / Kicker
        p0 = tf.paragraphs[0]
        p0.text = category.upper()
        p0.font.name = "Inter"
        p0.font.size = Pt(11)
        p0.font.bold = True
        p0.font.color.rgb = CYAN_BRIGHT
        p0.space_after = Pt(2)
        
        # Title
        p1 = tf.add_paragraph()
        p1.text = title
        p1.font.name = "Inter"
        p1.font.size = Pt(26)
        p1.font.bold = True
        p1.font.color.rgb = TEXT_PRIMARY
        
        if subhead:
            p1.space_after = Pt(2)
            p2 = tf.add_paragraph()
            p2.text = subhead
            p2.font.name = "Inter"
            p2.font.size = Pt(13)
            p2.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 1 — TITLE & TEAM
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    add_bg(s1)

    # Top Pill Badge
    badge = add_card(s1, Inches(4.3), Inches(1.2), Inches(4.73), Inches(0.45), border_color=CYAN, fill_color=RGBColor(15, 23, 42))
    btb = s1.shapes.add_textbox(Inches(4.3), Inches(1.25), Inches(4.73), Inches(0.35))
    btf = btb.text_frame
    bp = btf.paragraphs[0]
    bp.alignment = PP_ALIGN.CENTER
    bp.text = "HEC × PAK ANGELS GenAI — MIDTERM HACKATHON"
    bp.font.name = "Inter"
    bp.font.size = Pt(11)
    bp.font.bold = True
    bp.font.color.rgb = CYAN_BRIGHT

    # Main Headline
    tb_main = s1.shapes.add_textbox(Inches(1.0), Inches(2.1), Inches(11.33), Inches(2.2))
    tf_main = tb_main.text_frame
    tf_main.word_wrap = True
    
    p = tf_main.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "CampusVault"
    p.font.name = "Inter"
    p.font.size = Pt(56)
    p.font.bold = True
    p.font.color.rgb = TEXT_PRIMARY
    p.space_after = Pt(8)

    p2 = tf_main.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    p2.text = "Grounded Knowledge Engine"
    p2.font.name = "Inter"
    p2.font.size = Pt(22)
    p2.font.bold = True
    p2.font.color.rgb = CYAN_BRIGHT
    p2.space_after = Pt(4)

    p3 = tf_main.add_paragraph()
    p3.alignment = PP_ALIGN.CENTER
    p3.text = "Agentic RAG Engineered for University Exam Preparation"
    p3.font.name = "Inter"
    p3.font.size = Pt(16)
    p3.font.color.rgb = TEXT_MUTED

    # URL Pill Badge
    url_pill = add_card(s1, Inches(4.7), Inches(4.7), Inches(3.93), Inches(0.55), border_color=CYAN_BRIGHT, fill_color=RGBColor(2, 132, 199))
    utb = s1.shapes.add_textbox(Inches(4.7), Inches(4.78), Inches(3.93), Inches(0.4))
    utf = utb.text_frame
    up = utf.paragraphs[0]
    up.alignment = PP_ALIGN.CENTER
    up.text = "🌐 campusvault.ilyankhan.tech"
    up.font.name = "JetBrains Mono"
    up.font.size = Pt(14)
    up.font.bold = True
    up.font.color.rgb = TEXT_PRIMARY

    # Team Members Bar
    team_members = [
        ("Shahzaib Ali", "Product Lead"),
        ("Ali Hussain", "UI/UX & RAG"),
        ("Aqsa Sarfaraz", "Dataset & QA"),
        ("Arfa Rehman", "Backend Eng"),
        ("Zainab Faiz", "Frontend Eng"),
        ("Warda Nadeem", "Lead Presenter")
    ]
    
    card_w = Inches(1.85)
    card_gap = Inches(0.12)
    start_left = Inches(0.8)
    top_y = Inches(5.8)

    for i, (name, role) in enumerate(team_members):
        cur_left = start_left + i * (card_w + card_gap)
        add_card(s1, cur_left, top_y, card_w, Inches(1.0), border_color=CARD_BORDER, fill_color=CARD_BG)
        
        tb_m = s1.shapes.add_textbox(cur_left, top_y + Inches(0.12), card_w, Inches(0.75))
        tf_m = tb_m.text_frame
        tf_m.word_wrap = True
        tf_m.margin_left = tf_m.margin_right = 0
        
        pm1 = tf_m.paragraphs[0]
        pm1.alignment = PP_ALIGN.CENTER
        pm1.text = name
        pm1.font.name = "Inter"
        pm1.font.size = Pt(13)
        pm1.font.bold = True
        pm1.font.color.rgb = TEXT_PRIMARY
        pm1.space_after = Pt(2)
        
        pm2 = tf_m.add_paragraph()
        pm2.alignment = PP_ALIGN.CENTER
        pm2.text = role
        pm2.font.name = "Inter"
        pm2.font.size = Pt(10)
        pm2.font.color.rgb = CYAN_BRIGHT

    # =========================================================================
    # SLIDE 2 — THE PROBLEM
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_bg(s2)
    add_header(s2, "The Problem", "AI Tools Hallucinate. Engineering Students Pay the Price.", "Why standard LLMs and basic keyword search fail university exams.")

    # Left Column: 5 Problem Cards
    left_x = Inches(0.8)
    left_w = Inches(6.8)
    card_h = Inches(0.82)
    gap = Inches(0.12)
    start_y = Inches(1.8)

    problems = [
        ("🔴 Zero Grounding", "ChatGPT invents formulas, fakes algorithm traces & ignores course grading rubrics."),
        ("🔴 No Citations", "Students cannot verify a single mathematical step or check if code matches lab specs."),
        ("🔴 Basic RAG Isn't The Fix", "Naive keyword search + blindly pasting text chunks creates fragmented, broken answers."),
        ("🔴 400+ Pages of PDF Chaos", "Syllabus materials scattered across ephemeral WhatsApp drives & handwritten notes."),
        ("🔴 Knowledge Dies at Graduation", "Senior exam notes, solved papers & lab implementations vanish every semester.")
    ]

    for i, (head, desc) in enumerate(problems):
        cy = start_y + i * (card_h + gap)
        add_card(s2, left_x, cy, left_w, card_h, border_color=RGBColor(239, 68, 68), fill_color=CARD_BG)
        
        tb_p = s2.shapes.add_textbox(left_x + Inches(0.18), cy + Inches(0.1), left_w - Inches(0.36), card_h - Inches(0.2))
        tf_p = tb_p.text_frame
        tf_p.word_wrap = True
        tf_p.margin_left = tf_p.margin_top = tf_p.margin_right = tf_p.margin_bottom = 0
        
        p = tf_p.paragraphs[0]
        p.text = head + " — "
        p.font.name = "Inter"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = RED
        
        r = p.add_run()
        r.text = desc
        r.font.name = "Inter"
        r.font.size = Pt(11)
        r.font.bold = False
        r.font.color.rgb = TEXT_PRIMARY

    # Right Column: Symptom Card / Mock Hallucination Box
    right_x = Inches(7.8)
    right_w = Inches(4.7)
    right_h = Inches(4.6)
    
    add_card(s2, right_x, start_y, right_w, right_h, border_color=RGBColor(239, 68, 68), fill_color=RGBColor(20, 10, 15))
    
    tb_mock = s2.shapes.add_textbox(right_x + Inches(0.25), start_y + Inches(0.2), right_w - Inches(0.5), right_h - Inches(0.4))
    tf_mock = tb_mock.text_frame
    tf_mock.word_wrap = True
    
    p = tf_mock.paragraphs[0]
    p.text = "GENERIC AI (MOCK RESPONSE)"
    p.font.name = "Inter"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = RED
    p.space_after = Pt(8)

    p = tf_mock.add_paragraph()
    p.text = "Query: 'Calculate usable host IPs for CIDR /26 according to CSE-305 exam rubric.'"
    p.font.name = "JetBrains Mono"
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_MUTED
    p.space_after = Pt(10)

    p = tf_mock.add_paragraph()
    p.text = "ChatGPT Answer:\n'In a /26 network, total host bits = 32 - 26 = 6. Usable hosts = 2^6 = 64 hosts.'"
    p.font.name = "JetBrains Mono"
    p.font.size = Pt(11)
    p.font.color.rgb = RGBColor(254, 202, 202)
    p.space_after = Pt(12)

    p = tf_mock.add_paragraph()
    p.text = "✗ CRITICAL EXAM ERROR:\nForgot to subtract 2 reserved addresses (Network ID & Broadcast).\nCorrect answer is 62, not 64!\n✗ ZERO CITATION · ✗ STUDENT LOSES MARKS"
    p.font.name = "Inter"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = RED

    # =========================================================================
    # SLIDE 3 — THE SOLUTION (WHY AGENTIC RAG)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_bg(s3)
    add_header(s3, "The Solution", "Agentic RAG — A Planner, a Gatekeeper & a Parser Working Together", "Replacing naive vector search with a multi-step autonomous cognitive pipeline.")

    # Comparison Table
    table_shape = s3.shapes.add_table(5, 3, Inches(0.8), Inches(1.8), Inches(11.73), Inches(4.3))
    table = table_shape.table
    table.columns[0].width = Inches(2.5)
    table.columns[1].width = Inches(4.5)
    table.columns[2].width = Inches(4.73)

    headers = ["DIMENSION", "BASIC / NAIVE RAG", "CAMPUSVAULT AGENTIC RAG ✨"]
    for col_idx, h in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(15, 23, 42) if col_idx < 2 else RGBColor(2, 132, 199)
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = "Inter"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = TEXT_PRIMARY

    rows_data = [
        ("Retrieval Strategy", "Blind keyword or flat cosine search against all documents.", "🧭 Agentic Query Router identifies subject (6 courses) & syllabus week before retrieving."),
        ("Confidence Gate", "None. Always produces an answer even when context is irrelevant.", "🛡️ Strict Confidence Threshold (>= 0.65). Honestly flags unverified fallback queries."),
        ("Chunking Boundary", "Fixed character splits (e.g. 500 chars). Breaks formulas & code.", "📐 AST-Aware Chunking respects C++/Python functions & LaTeX equation blocks intact."),
        ("Source Citations", "Opaque or non-existent. Student cannot inspect original note.", "📄 Raw Peer Note Inspection with transparent similarity match % & verified metadata.")
    ]

    for row_idx, (dim, naive, agentic) in enumerate(rows_data, 1):
        cell_dim = table.cell(row_idx, 0)
        cell_dim.fill.solid()
        cell_dim.fill.fore_color.rgb = CARD_BG
        p = cell_dim.text_frame.paragraphs[0]
        p.text = dim
        p.font.name = "Inter"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = CYAN_BRIGHT

        cell_naive = table.cell(row_idx, 1)
        cell_naive.fill.solid()
        cell_naive.fill.fore_color.rgb = CARD_BG
        p = cell_naive.text_frame.paragraphs[0]
        p.text = naive
        p.font.name = "Inter"
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MUTED

        cell_agentic = table.cell(row_idx, 2)
        cell_agentic.fill.solid()
        cell_agentic.fill.fore_color.rgb = RGBColor(20, 30, 50)
        p = cell_agentic.text_frame.paragraphs[0]
        p.text = agentic
        p.font.name = "Inter"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_PRIMARY

    # Footer Badge
    fb = add_card(s3, Inches(0.8), Inches(6.3), Inches(11.73), Inches(0.55), border_color=EMERALD, fill_color=RGBColor(10, 30, 25))
    ftb = s3.shapes.add_textbox(Inches(0.8), Inches(6.35), Inches(11.73), Inches(0.45))
    fp = ftb.text_frame.paragraphs[0]
    fp.alignment = PP_ALIGN.CENTER
    fp.text = "🎯 6 Engineering Subjects  ·  16-Week Curriculum Mapping  ·  Real-Time KaTeX LaTeX Math Engine"
    fp.font.name = "Inter"
    fp.font.size = Pt(12)
    fp.font.bold = True
    fp.font.color.rgb = EMERALD

    # =========================================================================
    # SLIDE 4 — ARCHITECTURE PIPELINE
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_bg(s4)
    add_header(s4, "System Architecture", "From Student Question to Grounded Answer — 6 Pipeline Nodes", "Complete end-to-end communication topology with zero blind spots.")

    nodes = [
        ("1. Student Query", "React UI (Vercel)\nUniversal input + subject auto-detect"),
        ("2. Query Router", "FastAPI (Render)\nClassifies course & 16-wk syllabus target"),
        ("3. FastEmbed ONNX", "384-dim Dense Vectors\nLocal CPU inference, $0 API cost"),
        ("4. pgvector Hybrid", "PostgreSQL DB\nCosine distance + keyword search <20ms"),
        ("5. Confidence Gate", "Score Threshold >= 0.65\nGrounded vs General Mode decision"),
        ("6. Groq Llama 3.3", "70B Versatile LLM\nReal-time SSE token stream + KaTeX math")
    ]

    card_w4 = Inches(1.8)
    gap4 = Inches(0.18)
    left_start4 = Inches(0.8)
    card_y4 = Inches(1.8)
    card_h4 = Inches(3.8)

    for i, (ntitle, ndesc) in enumerate(nodes):
        cx = left_start4 + i * (card_w4 + gap4)
        border_c = EMERALD if i == 4 else CYAN if i == 1 else CARD_BORDER
        fill_c = RGBColor(15, 35, 30) if i == 4 else CARD_BG
        
        add_card(s4, cx, card_y4, card_w4, card_h4, border_color=border_c, fill_color=fill_c)
        
        tb = s4.shapes.add_textbox(cx + Inches(0.1), card_y4 + Inches(0.2), card_w4 - Inches(0.2), card_h4 - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = ntitle
        p.font.name = "Inter"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = EMERALD if i == 4 else CYAN_BRIGHT
        p.space_after = Pt(10)
        
        p2 = tf.add_paragraph()
        p2.text = ndesc
        p2.font.name = "Inter"
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_PRIMARY

    # Bottom Stat Chips
    stat_chips = [
        ("< 20ms", "Vector Search Latency"),
        ("384-dim", "FastEmbed ONNX Embeddings"),
        ("$0 API Cost", "Local Embedding Pipeline"),
        ("< 500ms", "Time to First Token (TTFT)")
    ]
    chip_w = Inches(2.78)
    chip_gap = Inches(0.2)
    chip_y = Inches(5.9)

    for i, (val, lbl) in enumerate(stat_chips):
        cx = Inches(0.8) + i * (chip_w + chip_gap)
        add_card(s4, cx, chip_y, chip_w, Inches(0.9), border_color=CARD_BORDER, fill_color=RGBColor(15, 23, 42))
        
        tb = s4.shapes.add_textbox(cx, chip_y + Inches(0.1), chip_w, Inches(0.7))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.text = val
        p.font.name = "JetBrains Mono"
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = CYAN_BRIGHT
        p.space_after = Pt(2)
        
        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        p2.text = lbl
        p2.font.name = "Inter"
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 5 — THE CONFIDENCE GATE (JUDGE CRITICAL)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_bg(s5)
    add_header(s5, "The Agentic Mechanism", "The Confidence Gate — It Never Pretends to be Grounded", "Why autonomous verification and honest refusal define true Agentic RAG.")

    # Left Column: Dual Decision Outcome Cards
    left_x5 = Inches(0.8)
    left_w5 = Inches(5.6)
    
    # Grounded Mode Card (Top)
    add_card(s5, left_x5, Inches(1.8), left_w5, Inches(2.2), border_color=EMERALD, fill_color=RGBColor(10, 30, 25))
    tb_g = s5.shapes.add_textbox(left_x5 + Inches(0.2), Inches(1.95), left_w5 - Inches(0.4), Inches(1.9))
    tf_g = tb_g.text_frame
    tf_g.word_wrap = True
    
    p = tf_g.paragraphs[0]
    p.text = "🟢 GROUNDED MODE (Similarity Score ≥ 0.65)"
    p.font.name = "Inter"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = EMERALD
    p.space_after = Pt(6)

    p2 = tf_g.add_paragraph()
    p2.text = "• Injects verified senior peer notes & syllabus context into LLM.\n• Formats math derivations with KaTeX & displays exact source chunk citation.\n• Student can inspect raw note & view cosine similarity match percentage."
    p2.font.name = "Inter"
    p2.font.size = Pt(11)
    p2.font.color.rgb = TEXT_PRIMARY

    # General Mode Card (Bottom)
    add_card(s5, left_x5, Inches(4.2), left_w5, Inches(2.2), border_color=AMBER, fill_color=RGBColor(35, 25, 10))
    tb_a = s5.shapes.add_textbox(left_x5 + Inches(0.2), Inches(4.35), left_w5 - Inches(0.4), Inches(1.9))
    tf_a = tb_a.text_frame
    tf_a.word_wrap = True
    
    p = tf_a.paragraphs[0]
    p.text = "🟡 GENERAL AI MODE (Similarity Score < 0.65)"
    p.font.name = "Inter"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = AMBER
    p.space_after = Pt(6)

    p2 = tf_a.add_paragraph()
    p2.text = "• Explicitly discloses: 'I am operating in General AI Mode — could not find verified peer notes for this topic.'\n• Answers parametrically without fabricating fake note citations.\n• Eliminates silent hallucination: complete transparency."
    p2.font.name = "Inter"
    p2.font.size = Pt(11)
    p2.font.color.rgb = TEXT_PRIMARY

    # Right Column: Live Proof Screenshot (KaTeX Math + Citation)
    right_x5 = Inches(6.7)
    right_w5 = Inches(5.8)
    add_card(s5, right_x5, Inches(1.8), right_w5, Inches(4.6), border_color=CYAN_BRIGHT, fill_color=CARD_BG)
    
    # Embed Screenshot 02
    img2_path = os.path.join(SCREENSHOTS_DIR, "02_desktop_grounded_answer.png")
    if os.path.exists(img2_path):
        s5.shapes.add_picture(img2_path, right_x5 + Inches(0.15), Inches(2.0), width=right_w5 - Inches(0.3))

    # =========================================================================
    # SLIDE 6 — TECH STACK & INGESTION PIPELINE
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_bg(s6)
    add_header(s6, "Engineering Deep Dive", "Production Tech Stack & AST-Aware Ingestion Pipeline", "High-throughput architecture built for developer-grade precision and zero API cost.")

    # Left: Stack Table
    left_x6 = Inches(0.8)
    left_w6 = Inches(5.6)
    
    table6_shape = s6.shapes.add_table(6, 2, left_x6, Inches(1.8), left_w6, Inches(4.6))
    table6 = table6_shape.table
    table6.columns[0].width = Inches(2.0)
    table6.columns[1].width = Inches(3.6)

    stack_rows = [
        ("Frontend UI", "React 18, TypeScript, Vite, Tailwind CSS"),
        ("Backend Server", "FastAPI (Python 3.14) on Render"),
        ("LLM Inference", "Groq Llama 3.3 70B (SSE Stream)"),
        ("Embeddings Engine", "FastEmbed ONNX (384-dim dense vectors)"),
        ("Vector Storage", "PostgreSQL + pgvector (Cosine index)"),
        ("Document Parsing", "AST-aware chunker + pdfplumber OCR")
    ]

    for r_idx, (layer, tech) in enumerate(stack_rows):
        cell_l = table6.cell(r_idx, 0)
        cell_l.fill.solid()
        cell_l.fill.fore_color.rgb = RGBColor(15, 23, 42)
        p = cell_l.text_frame.paragraphs[0]
        p.text = layer
        p.font.name = "Inter"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = CYAN_BRIGHT

        cell_t = table6.cell(r_idx, 1)
        cell_t.fill.solid()
        cell_t.fill.fore_color.rgb = CARD_BG
        p = cell_t.text_frame.paragraphs[0]
        p.text = tech
        p.font.name = "Inter"
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_PRIMARY

    # Right: AST Chunking Card + Upload Modal
    right_x6 = Inches(6.7)
    right_w6 = Inches(5.8)
    
    # Card 1: AST Chunking Explainer
    add_card(s6, right_x6, Inches(1.8), right_w6, Inches(1.6), border_color=CYAN_BRIGHT, fill_color=RGBColor(15, 23, 42))
    tb_ast = s6.shapes.add_textbox(right_x6 + Inches(0.2), Inches(1.9), right_w6 - Inches(0.4), Inches(1.4))
    tf_ast = tb_ast.text_frame
    tf_ast.word_wrap = True
    
    p = tf_ast.paragraphs[0]
    p.text = "📐 AST-AWARE INGESTION ENGINE"
    p.font.name = "Inter"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = CYAN_BRIGHT
    p.space_after = Pt(4)

    p2 = tf_ast.add_paragraph()
    p2.text = "Parses code function boundaries (C++/Python) & equation blocks ($$...$$) before vectorizing. Math derivations & class algorithms are never severed mid-step."
    p2.font.name = "Inter"
    p2.font.size = Pt(10)
    p2.font.color.rgb = TEXT_PRIMARY

    # Embed Screenshot 04 (Upload Modal)
    img4_path = os.path.join(SCREENSHOTS_DIR, "04_desktop_upload_modal.png")
    if os.path.exists(img4_path):
        s6.shapes.add_picture(img4_path, right_x6, Inches(3.6), width=right_w6)

    # =========================================================================
    # SLIDE 7 — LIVE DEMO & IMPACT (CLOSING)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_bg(s7)
    add_header(s7, "Production Deployment & Impact", "See It Live: campusvault.ilyankhan.tech", "Ready for university deployment with zero hallucination and verified citations.")

    # Top: Screenshot of Launchpad with Desktop UI
    img1_path = os.path.join(SCREENSHOTS_DIR, "01_desktop_launchpad.png")
    if os.path.exists(img1_path):
        s7.shapes.add_picture(img1_path, Inches(0.8), Inches(1.7), width=Inches(8.0))

    # Right Inset: Mobile View Screenshot
    img5_path = os.path.join(SCREENSHOTS_DIR, "05_mobile_workstation.png")
    if os.path.exists(img5_path):
        s7.shapes.add_picture(img5_path, Inches(9.1), Inches(1.7), width=Inches(3.43))

    # Bottom Stat Bar & CTA
    add_card(s7, Inches(0.8), Inches(5.8), Inches(11.73), Inches(1.2), border_color=CYAN_BRIGHT, fill_color=RGBColor(15, 23, 42))
    
    tb_c = s7.shapes.add_textbox(Inches(1.0), Inches(5.9), Inches(11.33), Inches(1.0))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True
    
    p = tf_c.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "🎯 6 Engineering Subjects  ·  16-Week Curriculum Map  ·  AST-Safe Chunking  ·  $0 API Cost"
    p.font.name = "Inter"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = CYAN_BRIGHT
    p.space_after = Pt(4)

    p2 = tf_c.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    p2.text = "▶ Full Live Demo Video: Pipeline tracing, mobile drawer & source inspection attached."
    p2.font.name = "Inter"
    p2.font.size = Pt(11)
    p2.font.color.rgb = TEXT_PRIMARY
    p2.space_after = Pt(2)

    p3 = tf_c.add_paragraph()
    p3.alignment = PP_ALIGN.CENTER
    p3.text = "CampusVault — Grounded Knowledge Engine. Ask With Proof."
    p3.font.name = "Inter"
    p3.font.size = Pt(12)
    p3.font.bold = True
    p3.font.color.rgb = EMERALD

    # Save to Downloads & docs
    out_file1 = "/home/ilyan/Downloads/CampusVault Pitch Slide Deck.pptx"
    out_file2 = "/home/ilyan/ilmai/docs/CampusVault Pitch Slide Deck.pptx"
    prs.save(out_file1)
    prs.save(out_file2)
    print("SUCCESS: 7-Slide Blueprint Presentation generated at:")
    print("  ->", out_file1)
    print("  ->", out_file2)

if __name__ == "__main__":
    create_deck()
