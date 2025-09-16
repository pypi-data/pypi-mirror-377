# ==================== IMPORTS ====================
import cv2
import numpy as np
import json
import os
import re
import base64
import time
import shutil
import textwrap
from io import BytesIO
from PIL import Image
from getpass import getpass
from typing import List, Tuple, Dict, Any, Optional

# Imports for Google Colab
from google.colab import files
from google.colab.patches import cv2_imshow
from google.colab import output
from IPython.display import display, Image as IPImage, clear_output, HTML

# Imports for Stage 3 (LLM)
try:
    import google.generativeai as genai
except ImportError:
    print("Warning: 'google-generativeai' not found. Stage 3 will not be available.")
    print("Please run: !pip install -q google-generativeai")

# ==================== UTILITY FUNCTIONS ====================
def cleanup_pipeline():
    """Removes all generated files and folders from the pipeline."""
    print("🧹 Cleaning up pipeline artifacts...")
    items_to_remove = [
        'uploads',
        'bounded_images',
        'final_outputs',
        'coords.json'
    ]
    for item in items_to_remove:
        try:
            if os.path.exists(item):
                if os.path.isdir(item):
                    shutil.rmtree(item)
                    print(f"  - Removed directory: {item}/")
                else:
                    os.remove(item)
                    print(f"  - Removed file: {item}")
        except Exception as e:
            print(f"  - Error removing {item}: {e}")
    print("✅ Cleanup complete.")

def pretty_print_page_with_image(json_path: str):
    """
    Pretty prints the content of a final JSON file and displays its
    corresponding annotated image.
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File '{json_path}' not found.")
        return

    row_id = os.path.splitext(os.path.basename(json_path))[0]
    print("=" * 100)
    print(f"📄 DOCUMENT PREVIEW: {row_id}")
    print("=" * 100)

    header = data.get("Page header", "") or "(none)"
    page_text = data.get("Page text", "") or "(none)"
    footer = data.get("Page footer", "") or "(none)"

    print(f"📋 HEADER:\n---\n{textwrap.fill(header, 100)}\n")
    print(f"📖 PAGE TEXT:\n---\n{textwrap.fill(page_text, 100)}")
    print(f"\n📝 FOOTER:\n---\n{textwrap.fill(footer, 100)}\n")

    table_bbox = data.get("table_bbox", [])
    image_bbox = data.get("image_bbox", [])

    print("🟥 TABLE BBOX ([ymin, xmin, ymax, xmax]):")
    print("---" if table_bbox else "(none)")
    if table_bbox:
        for i, bbox in enumerate(table_bbox, 1): print(f"  Table {i}: {bbox}")

    print("\n🟩 IMAGE BBOX ([ymin, xmin, ymax, xmax]):")
    print("---" if image_bbox else "(none)")
    if image_bbox:
        for i, bbox in enumerate(image_bbox, 1): print(f"  Image {i}: {bbox}")

    img_path = os.path.join('bounded_images', f"{row_id}.jpg")
    if os.path.exists(img_path):
        print(f"\n📸 CORRESPONDING ANNOTATED IMAGE:")
        cv2_imshow(cv2.imread(img_path))
    else:
        print(f"\n⚠️ Annotated image not found at: {img_path}")
    print("=" * 100)

def show_comparison_view(json_path: str, mode: str = "ir", uploads_dir: str = 'uploads', coords_file: str = 'coords.json'):
    """
    Renders a flexible, side-by-side HTML view of document annotations.

    Args:
        json_path (str): Path to the JSON annotation file (e.g., 'final_outputs/1.json').
        mode (str): View mode. 
                    "ir" = image vs rendered text
                    "ij" = image vs raw JSON
                    "jr" = raw JSON vs rendered text
        uploads_dir (str): Directory containing original images (default: 'uploads').
        coords_file (str): File containing coordinate mappings (default: 'coords.json').
    """
    # Map short mode codes to panels
    mode_map = {
        "ir": ("image", "rendered_text"),
        "ij": ("image", "raw_json"),
        "jr": ("raw_json", "rendered_text")
    }
    left_panel, right_panel = mode_map.get(mode, ("image", "rendered_text"))

    print(f"--- 🖼️  Generating comparison: [{left_panel.upper()}] vs [{right_panel.upper()}] for {os.path.basename(json_path)} ---")

    # --- 1. Load JSON Data ---
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: JSON file not found at '{json_path}'")
        return
    except json.JSONDecodeError:
        print(f"❌ Error: Could not parse the JSON file. It might be malformed: '{json_path}'")
        return

    # --- 2. Prepare All Possible Content Blocks ---
    image_html, raw_json_html, rendered_text_html = "", "", ""

    # A. Prepare Image HTML
    if 'image' in [left_panel, right_panel]:
        row_id = os.path.splitext(os.path.basename(json_path))[0]
        img_path = os.path.join('bounded_images', f"{row_id}.jpg")

        if os.path.exists(img_path):
            try:
                image = cv2.imread(img_path)
                image_rgb = image
                _, buffer = cv2.imencode('.jpg', image_rgb)
                base64_image = base64.b64encode(buffer).decode('utf-8')
                image_html = f'''
                    <h3 class="panel-title">Annotated Page Image</h3>
                    <div class="inner-card">
                        <img src="data:image/jpeg;base64,{base64_image}" style="width: 100%; border: 1px solid #ccc;">
                    </div>
                '''
            except Exception as e:
                image_html = f"<p style='color:red;'>⚠️ Could not load image: {e}</p>"
        else:
            image_html = f"<p style='color:red;'>❌ Image not found at {img_path}</p>"

    # B. Prepare Raw JSON HTML
    if 'raw_json' in [left_panel, right_panel]:
        pretty_json = json.dumps(data, indent=2, ensure_ascii=False)
        escaped_json = pretty_json.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        raw_json_html = f'''
            <h3 class="panel-title">Raw JSON Content</h3>
            <div class="inner-card">
                <pre style="white-space: pre-wrap; word-wrap: break-word;"><code>{escaped_json}</code></pre>
            </div>
        '''

    # C. Prepare Rendered Text HTML
    if 'rendered_text' in [left_panel, right_panel]:
        header = (data.get("Page header") or "").strip()
        page_text = (data.get("Page text") or "No 'Page text' found in JSON.").strip()
        footer = (data.get("Page footer") or "").strip()

        processed_text = page_text.replace('\\(', '$').replace('\\)', '$')
        processed_text = processed_text.replace('\\[', '$$').replace('\\]', '$$')

        pattern = re.compile(r"\$\$(.*?)\$\$\s*?\n\s*?\((\d+)\)", re.DOTALL)
        final_text = pattern.sub(r"$$\1 \\tag{\2}$$", processed_text)
        final_text = final_text.replace('\n', '<br>')
        
        rendered_parts = []
        if header:
            rendered_parts.append(f'<div class="header-section">{header}</div>')
        rendered_parts.append(f'<div class="rendered-body">{final_text}</div>')
        if footer:
            rendered_parts.append(f'<div class="footer-section">{footer}</div>')
        
        rendered_content = ''.join(rendered_parts)

        rendered_text_html = f'''
            <h3 class="panel-title">Rendered Document Preview</h3>
            <div class="inner-card">{rendered_content}</div>
        '''

    # --- 3. Assemble the Final HTML View ---
    content_map = {
        'image': image_html,
        'raw_json': raw_json_html,
        'rendered_text': rendered_text_html
    }
    left_html = content_map.get(left_panel, "Invalid left_panel choice")
    right_html = content_map.get(right_panel, "Invalid right_panel choice")

    mathjax_scripts = ""
    if 'rendered_text' in [left_panel, right_panel]:
        mathjax_scripts = """
        <script>
          window.MathJax = {
            tex: { inlineMath: [['$', '$'], ['\\(', '\\)']], tags: 'ams', tagSide: 'right', tagIndent: '0.8em' },
            chtml: { scale: 1.05 }
          };
        </script>
        <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        """

    full_html = f"""
    <html><head>{mathjax_scripts}<style>
        .container {{ display: flex; gap: 20px; font-family: 'Times New Roman', 'Times', serif; }}
        
        .panel {{ 
            flex: 1; 
            border: 1px solid #ddd; 
            padding: 15px; 
            border-radius: 8px; 
            overflow-x: auto; 
            background-color: #fdfdfd; 
        }}
        
        .panel-title {{
            text-align: center;
            font-family: sans-serif;
            margin: 0 0 15px 0;
            font-weight: 600;
        }}

        .inner-card {{
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            background: #fff;
        }}
        
        .document-container {{ margin: 0; padding: 0; }}
        
        .rendered-body {{ 
            text-align: justify; 
            line-height: 1.8; 
            font-size: 18px; 
            color: #000;
        }}
        
        .header-section {{
            margin-bottom: 15px;
            font-size: 18px;
            color: #000;
            text-align: left;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            background: #fafafa;
        }}
        
        .footer-section {{
            margin-top: 20px;
            font-size: 18px;
            color: #000;
            text-align: center;
            line-height: 1.2;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            background: #fafafa;
        }}
        
        .document-container > *:last-child {{
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }}
        
        mjx-container[jax="CHTML"][display="true"] {{ margin: 1.5em 0; }}
    </style></head><body><div class="container">
        <div class="panel">{left_html}</div>
        <div class="panel">{right_html}</div>
    </div></body></html>
    """
    display(HTML(full_html))


# ==================== HELPER & EDITOR FUNCTIONS ====================

def xywh_to_yminmax(box: tuple) -> List[int]:
    """Converts (x, y, w, h) to [ymin, xmin, ymax, xmax]."""
    x, y, w, h = box
    return [y, x, y + h, x + w]

def yminmax_to_xywh(box: list) -> List[int]:
    """Converts [ymin, xmin, ymax, xmax] to [x, y, w, h]."""
    ymin, xmin, ymax, xmax = box
    return [xmin, ymin, xmax - xmin, ymax - ymin]

def detect_tables(image: np.ndarray) -> List[List[int]]:
    """Detects tables in an image. Returns xywh format."""
    boxes = []
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    binary = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, -2)
    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    h_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, h_kernel, iterations=2)
    v_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, v_kernel, iterations=2)
    mask = cv2.add(h_lines, v_lines)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        if cv2.contourArea(c) > 2000:
            x, y, w, h = cv2.boundingRect(c)
            if w > 50 and h > 50:
                boxes.append([x, y, w, h])
    return boxes

def detect_image_regions(image: np.ndarray, min_area_percentage=1.5) -> List[List[int]]:
    """Detects image regions. Returns xywh format."""
    h, w, _ = image.shape
    min_area = (min_area_percentage / 100) * (h * w)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edged = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 100, 200)
    contours, _ = cv2.findContours(cv2.dilate(edged, None, iterations=2), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for c in contours:
        if cv2.contourArea(c) > min_area:
            x, y, w_box, h_box = cv2.boundingRect(c)
            if 0.2 < (w_box / float(h_box) if h_box > 0 else 0) < 5.0 and w_box > 80 and h_box > 80:
                boxes.append([x, y, w_box, h_box])
    return boxes

def create_annotated_image(
    image: np.ndarray,
    table_boxes: List[List[int]],
    image_boxes: List[List[int]],
    column_boxes: List[List[int]] = None,
    header_boxes: List[List[int]] = None,
    footer_boxes: List[List[int]] = None
) -> np.ndarray:
    """Creates annotated image with all bounding box types."""
    annotated_img = image.copy()

    # Set defaults
    column_boxes = column_boxes or []
    header_boxes = header_boxes or []
    footer_boxes = footer_boxes or []

    # Draw table boxes (red)
    for i, box in enumerate(table_boxes):
        if any(box):  # Skip empty boxes
            x, y, w, h = box
            cv2.rectangle(annotated_img, (x, y), (x + w, y + h), (0, 0, 255), 3)
            cv2.putText(annotated_img, f"Table {i+1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    # Draw image boxes (green)
    for i, box in enumerate(image_boxes):
        if any(box):  # Skip empty boxes
            x, y, w, h = box
            cv2.rectangle(annotated_img, (x, y), (x + w, y + h), (0, 255, 0), 3)
            cv2.putText(annotated_img, f"Image {i+1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Draw column boxes (blue)
    for i, box in enumerate(column_boxes):
        if any(box):  # Skip empty boxes
            x, y, w, h = box
            cv2.rectangle(annotated_img, (x, y), (x + w, y + h), (255, 0, 0), 3)
            cv2.putText(annotated_img, f"Column {i+1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    # Draw header boxes (cyan)
    for i, box in enumerate(header_boxes):
        if any(box):  # Skip empty boxes
            x, y, w, h = box
            cv2.rectangle(annotated_img, (x, y), (x + w, y + h), (255, 255, 0), 3)
            cv2.putText(annotated_img, f"Header {i+1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)

    # Draw footer boxes (magenta)
    for i, box in enumerate(footer_boxes):
        if any(box):  # Skip empty boxes
            x, y, w, h = box
            cv2.rectangle(annotated_img, (x, y), (x + w, y + h), (255, 0, 255), 3)
            cv2.putText(annotated_img, f"Footer {i+1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 255), 2)

    return annotated_img

def create_context_image(
    image: np.ndarray,
    context_table_boxes: List[Tuple[List[int], int]],  # (box, original_index)
    context_image_boxes: List[Tuple[List[int], int]],   # (box, original_index)
    context_column_boxes: List[Tuple[List[int], int]] = None,
    context_header_boxes: List[Tuple[List[int], int]] = None,
    context_footer_boxes: List[Tuple[List[int], int]] = None
) -> np.ndarray:
    """Creates image with context boxes (all boxes except the one being edited)."""
    context_img = image.copy()

    # Set defaults
    context_column_boxes = context_column_boxes or []
    context_header_boxes = context_header_boxes or []
    context_footer_boxes = context_footer_boxes or []

    # Draw context table boxes (red)
    for box, original_idx in context_table_boxes:
        if any(box):
            x, y, w, h = box
            cv2.rectangle(context_img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(context_img, f"Table {original_idx + 1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # Draw context image boxes (green)
    for box, original_idx in context_image_boxes:
        if any(box):
            x, y, w, h = box
            cv2.rectangle(context_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(context_img, f"Image {original_idx + 1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Draw context column boxes (blue)
    for box, original_idx in context_column_boxes:
        if any(box):
            x, y, w, h = box
            cv2.rectangle(context_img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(context_img, f"Column {original_idx + 1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    # Draw context header boxes (cyan)
    for box, original_idx in context_header_boxes:
        if any(box):
            x, y, w, h = box
            cv2.rectangle(context_img, (x, y), (x + w, y + h), (255, 255, 0), 2)
            cv2.putText(context_img, f"Header {original_idx + 1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    # Draw context footer boxes (magenta)
    for box, original_idx in context_footer_boxes:
        if any(box):
            x, y, w, h = box
            cv2.rectangle(context_img, (x, y), (x + w, y + h), (255, 0, 255), 2)
            cv2.putText(context_img, f"Footer {original_idx + 1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)

    return context_img

def interactive_editor(img: np.ndarray, initial_boxes: List[List[int]], editor_title: str) -> List[List[int]]:
    """Launches the HTML/JS editor for editing multiple bounding boxes."""

    _, buffer = cv2.imencode('.png', img)
    img_str = base64.b64encode(buffer).decode('utf-8')
    img_data_url = f'data:image/png;base64,{img_str}'

    # Accept multiple initial boxes (or empty list)
    initial_boxes = initial_boxes if initial_boxes else []
    boxes_json = json.dumps(initial_boxes)

    html_template = f"""
    <div style="border: 2px solid #ccc; padding: 10px; display: inline-block;">
        <h3 style="font-family: sans-serif;">{editor_title}</h3>
        <p style="font-family: sans-serif; margin-top: 0; line-height: 1.4;">
            <b>Click and drag</b> to draw a box.<br>
            <b>Click inside a box</b> to delete it.<br>
            <b>Use ↩️ Undo Last</b> to remove the most recent box.<br>
            You can draw multiple boxes before submitting.
        </p>
        <canvas id="editor-canvas" style="cursor: crosshair; border: 1px solid black;"></canvas>
        <br>
        <button id="undo-button" style="margin-top: 10px; font-size: 14px; padding: 6px 12px;">↩️ Undo Last</button>
        <button id="done-button" style="margin-top: 10px; font-size: 16px; padding: 8px 16px;">✅ Submit</button>
        <div id="status" style="margin-top: 10px; font-family: sans-serif; font-size: 14px;"></div>
    </div>
    <script>
    const canvas = document.getElementById('editor-canvas');
    const ctx = canvas.getContext('2d');
    const doneButton = document.getElementById('done-button');
    const undoButton = document.getElementById('undo-button');
    const status = document.getElementById('status');
    const img = new Image();

    window.finished = false;
    window.finalBoxes = [];
    let boxes = JSON.parse('{boxes_json}');
    let isDrawing = false;
    let startX, startY;

    function updateStatus(message) {{ status.textContent = message; }}

    img.onload = function() {{
        canvas.width = img.width;
        canvas.height = img.height;
        redraw();
        updateStatus('Image loaded. Ready for editing.');
    }};
    img.src = '{img_data_url}';

    function redraw() {{
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);
        ctx.strokeStyle = 'blue';
        ctx.lineWidth = 2;
        boxes.forEach(([x, y, w, h], idx) => {{
            ctx.strokeRect(x, y, w, h);
            ctx.fillStyle = "blue";
            ctx.font = "14px sans-serif";
            ctx.fillText(idx+1, x+5, y+20); // label each box
        }});
        updateStatus(`Current boxes: ${{boxes.length}}`);
    }}

    canvas.addEventListener('mousedown', (e) => {{
        const rect = canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        let boxClicked = -1;
        for (let i = boxes.length - 1; i >= 0; i--) {{
            const [x, y, w, h] = boxes[i];
            if (mouseX >= x && mouseX <= x + w && mouseY >= y && mouseY <= y + h) {{
                boxClicked = i;
                break;
            }}
        }}
        if (boxClicked !== -1) {{
            boxes.splice(boxClicked, 1);
            redraw();
            updateStatus('Box deleted.');
        }} else {{
            isDrawing = true;
            startX = mouseX;
            startY = mouseY;
            updateStatus('Drawing new box...');
        }}
    }});

    canvas.addEventListener('mousemove', (e) => {{
        if (!isDrawing) return;
        const rect = canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        redraw();
        ctx.strokeStyle = 'red';
        ctx.strokeRect(startX, startY, mouseX - startX, mouseY - startY);
    }});

    canvas.addEventListener('mouseup', (e) => {{
        if (!isDrawing) return;
        isDrawing = false;
        const rect = canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        const x = Math.min(startX, mouseX);
        const y = Math.min(startY, mouseY);
        const w = Math.abs(mouseX - startX);
        const h = Math.abs(mouseY - startY);
        if (w > 5 && h > 5) {{
            boxes.push([Math.round(x), Math.round(y), Math.round(w), Math.round(h)]);
        }}
        redraw();
    }});

    undoButton.addEventListener('click', () => {{
        if (boxes.length > 0) {{
            boxes.pop();
            redraw();
            updateStatus('Last box removed (undo).');
        }} else {{
            updateStatus('No boxes to undo.');
        }}
    }});

    doneButton.addEventListener('click', () => {{
        doneButton.textContent = '⏳ Submitting...';
        doneButton.disabled = true;
        canvas.style.cursor = 'default';
        window.finalBoxes = boxes;
        window.finished = true;
        updateStatus('✅ Submitted! Python is now processing...');
    }});
    </script>
    """

    display(HTML(html_template))
    print(f"\n✍️ Edit the {editor_title.lower()} above. Draw multiple boxes if needed, then click 'Submit'.")
    print("Waiting for manual correction... ⏳")

    final_boxes = None
    for _ in range(600):  # Wait for up to 5 minutes
        try:
            is_done = output.eval_js('window.finished')
            if is_done:
                final_boxes = output.eval_js('window.finalBoxes')
                break
        except Exception:
            pass
        time.sleep(0.5)

    clear_output(wait=False)
    if final_boxes is not None and len(final_boxes) > 0:
        print(f"✅ {len(final_boxes)} manual corrections received!")
        return final_boxes   # ✅ return all boxes now
    else:
        print("⚠️ No boxes submitted. Using original box(es)." if initial_boxes else "⚠️ No boxes submitted. No boxes will be saved.")
        return initial_boxes if initial_boxes else []

# ==================== STAGE 1: UPLOAD, DETECT, & EDIT ====================

def save_coords(row_id, filename, table_coords_xywh, image_coords_xywh, column_coords_xywh, header_coords_xywh, footer_coords_xywh):
    """Helper: Save current coords to coords.json after each edit (append mode)."""
    table_coords_yminmax = [xywh_to_yminmax(box) if any(box) else [] for box in table_coords_xywh]
    image_coords_yminmax = [xywh_to_yminmax(box) if any(box) else [] for box in image_coords_xywh]
    column_coords_yminmax = [xywh_to_yminmax(box) if any(box) else [] for box in column_coords_xywh]
    header_coords_yminmax = [xywh_to_yminmax(box) if any(box) else [] for box in header_coords_xywh]
    footer_coords_yminmax = [xywh_to_yminmax(box) if any(box) else [] for box in footer_coords_xywh]

    # Load existing coords if file exists
    if os.path.exists('coords.json'):
        with open('coords.json', 'r') as f:
            try:
                all_coords = json.load(f)
            except json.JSONDecodeError:
                all_coords = {}
    else:
        all_coords = {}

    # Update / overwrite only this row_id
    all_coords[row_id] = {
        "original_filename": filename,
        "tables": table_coords_yminmax,
        "images": image_coords_yminmax,
        "columns": column_coords_yminmax,
        "headers": header_coords_yminmax,
        "footers": footer_coords_yminmax
    }

    # Save back to file
    with open('coords.json', 'w') as f:
        json.dump(all_coords, f, indent=4)

    # Count only non-empty
    n_tables = sum(1 for b in table_coords_yminmax if b)
    n_images = sum(1 for b in image_coords_yminmax if b)
    n_columns = sum(1 for b in column_coords_yminmax if b)
    n_headers = sum(1 for b in header_coords_yminmax if b)
    n_footers = sum(1 for b in footer_coords_yminmax if b)

    print(f"💾 Updated coords.json → {row_id} ({n_tables} tables, {n_images} images, {n_columns} columns, {n_headers} headers, {n_footers} footers)")


def stage_1():
    """
    Handles multiple document uploads, detection, and interactive editing (batch mode).
    For each uploaded file:
      - Ask for row ID upfront (for all files at once).
      - Process files one by one with editing loop.
    """
    print("=" * 60 + "\nSTAGE 1: UPLOAD, DETECT, AND EDIT (BATCH)\n" + "=" * 60)

    # Create directories
    for folder in ['uploads', 'bounded_images']:
        os.makedirs(folder, exist_ok=True)

    # Upload files
    print("\n📤 Please upload your document images...")
    uploaded = files.upload()
    if not uploaded:
        print("❌ No files uploaded.")
        return

    # === Step 1: Ask for row IDs for all files ===
    row_ids = {}
    for i, filename in enumerate(uploaded.keys(), start=1):
        row_id = input(f"➡️ Enter a unique Row ID for '{filename}' (default: {os.path.splitext(filename)[0]}): ").strip()
        if not row_id:
            row_id = os.path.splitext(filename)[0]
        row_ids[filename] = row_id

    # === Step 2: Process each file one by one ===
    for filename, filedata in uploaded.items():
        filepath = os.path.join('uploads', filename)
        with open(filepath, 'wb') as f:
            f.write(filedata)

        row_id = row_ids[filename]
        print("\n" + "=" * 50)
        print(f"📄 Now processing file: {filename} (Row ID: {row_id})")
        print("=" * 50)

        # === Run single-file processing ===
        process_single_image(filename, filepath, row_id)


def process_single_image(filename, filepath, row_id):
    """
    Process a single image file with detection + interactive editing.
    Extracted from stage_1 so we can reuse for batch processing.
    """
    original_img = cv2.imread(filepath)

    # Resize for consistent display
    MAX_WIDTH = 1200
    original_h, original_w, _ = original_img.shape
    scale = MAX_WIDTH / original_w if original_w > MAX_WIDTH else 1.0
    display_w = int(original_w * scale)
    display_h = int(original_h * scale)
    display_img = cv2.resize(original_img, (display_w, display_h), interpolation=cv2.INTER_AREA)

    print("\n" + "=" * 50 + f"\nProcessing: {filename} (Row ID: {row_id})\n" + "=" * 50)
    print("Analyzing Document Content...")

    # Detect on original image, then scale for display
    table_coords_xywh = detect_tables(original_img)
    image_coords_xywh = detect_image_regions(original_img)
    column_coords_xywh = []  # Start empty, user will add manually
    header_coords_xywh = []  # Start empty, user will add manually  
    footer_coords_xywh = []  # Start empty, user will add manually

    table_coords_display = [[int(x * scale), int(y * scale), int(w * scale), int(h * scale)]
                            for x, y, w, h in table_coords_xywh]
    image_coords_display = [[int(x * scale), int(y * scale), int(w * scale), int(h * scale)]
                            for x, y, w, h in image_coords_xywh]
    column_coords_display = [[int(x * scale), int(y * scale), int(w * scale), int(h * scale)]
                            for x, y, w, h in column_coords_xywh]
    header_coords_display = [[int(x * scale), int(y * scale), int(w * scale), int(h * scale)]
                            for x, y, w, h in header_coords_xywh]
    footer_coords_display = [[int(x * scale), int(y * scale), int(w * scale), int(h * scale)]
                            for x, y, w, h in footer_coords_xywh]

    print(f"✅ Found {len(table_coords_xywh)} tables and {len(image_coords_xywh)} images.")

    # === LOOP FOR MULTIPLE EDITS ===
    while True:
        final_annotated = create_annotated_image(display_img, table_coords_display, image_coords_display, 
                                                column_coords_display, header_coords_display, footer_coords_display)
        comparison = np.hstack((display_img, final_annotated))
        cv2_imshow(comparison)

        time.sleep(0.5)

        print("\n" + "=" * 50)
        print("ACTION MENU")
        print("=" * 50)
        
        choice = input(
            "❓ What would you like to do?\n"
            f"  - To edit a table, type 'table 1' to 'table {len(table_coords_display)}'\n"
            f"  - To edit an image, type 'image 1' to 'image {len(image_coords_display)}'\n"
            f"  - To edit a column, type 'column 1' to 'column {len(column_coords_display)}'\n"
            f"  - To edit a header, type 'header 1' to 'header {len(header_coords_display)}'\n"
            f"  - To edit a footer, type 'footer 1' to 'footer {len(footer_coords_display)}'\n"
            "  - To ADD a new box, type 'add table', 'add image', 'add column', 'add header', or 'add footer'\n"
            "  - Type 'done' to approve all and finish.\n\n"
            "Your choice: "
        ).strip().lower()
        
        # === 1. Handle DONE ===
        if choice == "done":
            # ✅ Make sure we save results before breaking
            save_coords(row_id, filename, table_coords_xywh, image_coords_xywh, column_coords_xywh, header_coords_xywh, footer_coords_xywh)
            break

        # === 2. Handle ADD ===
        if choice.startswith("add "):
            _, add_type = choice.split()
            if add_type not in ["table", "image", "column", "header", "footer"]:
                print("❌ Invalid add type. Use 'add table', 'add image', 'add column', 'add header', or 'add footer'.")
                continue

            # Build context
            context_table_boxes = [(box, i) for i, box in enumerate(table_coords_display)]
            context_image_boxes = [(box, i) for i, box in enumerate(image_coords_display)]
            context_img = create_context_image(display_img, context_table_boxes, context_image_boxes)

            print(f"\n➕ Adding a new {add_type}...")
            corrected_boxes = interactive_editor(context_img, [], f"New {add_type.capitalize()} Editor")

            if corrected_boxes and len(corrected_boxes) > 0:
                for cb in corrected_boxes:
                    if add_type == "table":
                        table_coords_display.append(cb)
                        table_coords_xywh.append([int(v / scale) for v in cb])
                    elif add_type == "image":
                        image_coords_display.append(cb)
                        image_coords_xywh.append([int(v / scale) for v in cb])
                    elif add_type == "column":
                        column_coords_display.append(cb)
                        column_coords_xywh.append([int(v / scale) for v in cb])
                    elif add_type == "header":
                        header_coords_display.append(cb)
                        header_coords_xywh.append([int(v / scale) for v in cb])
                    elif add_type == "footer":
                        footer_coords_display.append(cb)
                        footer_coords_xywh.append([int(v / scale) for v in cb])
                save_coords(row_id, filename, table_coords_xywh, image_coords_xywh, column_coords_xywh, header_coords_xywh, footer_coords_xywh)
            else:
                print("⚠️ No box added.")

            continue
        
        # === 3. Handle EDIT ===
        try:
            if choice in ["table", "image"]:
                box_type = choice
                box_index = 0
                if box_type == "table" and len(table_coords_display) > 1:
                    print("❌ Multiple tables detected. Please specify 'table N'.")
                    continue
                if box_type == "image" and len(image_coords_display) > 1:
                    print("❌ Multiple images detected. Please specify 'image N'.")
                    continue
            else:
                parts = choice.split()
                if len(parts) != 2:
                    print("❌ Invalid format. Use 'table 1' or 'image 2'.")
                    continue
                box_type, box_index = parts[0], int(parts[1]) - 1
                if box_type not in ["table", "image", "column", "header", "footer"]:
                    print("❌ Invalid type. Use 'table', 'image', 'column', 'header', or 'footer'.")
                    continue

            # === TABLE EDITING ===
            if box_type == "table":
                if not (0 <= box_index < len(table_coords_display)):
                    print(f"❌ Table {box_index+1} doesn't exist.")
                    continue

                context_table_boxes = [(box, i) for i, box in enumerate(table_coords_display) if i != box_index]
                context_image_boxes = [(box, i) for i, box in enumerate(image_coords_display)]
                context_img = create_context_image(display_img, context_table_boxes, context_image_boxes)

                print(f"\n✏️ Editing Table {box_index+1}...")
                corrected_boxes = interactive_editor(context_img, [], f"Table {box_index+1} Editor")

                if corrected_boxes and len(corrected_boxes) > 0:
                    # Replace this one entry with multiple
                    new_display_boxes = []
                    new_xywh_boxes = []
                    for cb in corrected_boxes:
                        new_display_boxes.append(cb)
                        new_xywh_boxes.append([int(v / scale) for v in cb])

                    # Remove the old one and extend with new
                    table_coords_display.pop(box_index)
                    table_coords_xywh.pop(box_index)
                    table_coords_display.extend(new_display_boxes)
                    table_coords_xywh.extend(new_xywh_boxes)
                else:
                    # User deleted all boxes
                    table_coords_display[box_index] = [0, 0, 0, 0]
                    table_coords_xywh[box_index] = [0, 0, 0, 0]

                save_coords(row_id, filename, table_coords_xywh, image_coords_xywh, column_coords_xywh, header_coords_xywh, footer_coords_xywh)

            # === IMAGE EDITING ===
            elif box_type == "image":
                if not (0 <= box_index < len(image_coords_display)):
                    print(f"❌ Image {box_index+1} doesn't exist.")
                    continue

                context_table_boxes = [(box, i) for i, box in enumerate(table_coords_display)]
                context_image_boxes = [(box, i) for i, box in enumerate(image_coords_display) if i != box_index]
                context_img = create_context_image(display_img, context_table_boxes, context_image_boxes)

                print(f"\n✏️ Editing Image {box_index+1}...")
                corrected_boxes = interactive_editor(context_img, [image_coords_display[box_index]], f"Image {box_index+1} Editor")

                if corrected_boxes and len(corrected_boxes) > 0:
                    new_display_boxes = []
                    new_xywh_boxes = []
                    for cb in corrected_boxes:
                        new_display_boxes.append(cb)
                        new_xywh_boxes.append([int(v / scale) for v in cb])

                    image_coords_display.pop(box_index)
                    image_coords_xywh.pop(box_index)
                    image_coords_display.extend(new_display_boxes)
                    image_coords_xywh.extend(new_xywh_boxes)
                else:
                    image_coords_display[box_index] = [0, 0, 0, 0]
                    image_coords_xywh[box_index] = [0, 0, 0, 0]

                save_coords(row_id, filename, table_coords_xywh, image_coords_xywh, column_coords_xywh, header_coords_xywh, footer_coords_xywh)

            # === COLUMN EDITING ===
            elif box_type == "column":
                if not (0 <= box_index < len(column_coords_display)):
                    print(f"❌ Column {box_index+1} doesn't exist.")
                    continue

                context_table_boxes = [(box, i) for i, box in enumerate(table_coords_display)]
                context_image_boxes = [(box, i) for i, box in enumerate(image_coords_display)]
                context_column_boxes = [(box, i) for i, box in enumerate(column_coords_display) if i != box_index]
                context_header_boxes = [(box, i) for i, box in enumerate(header_coords_display)]
                context_footer_boxes = [(box, i) for i, box in enumerate(footer_coords_display)]
                context_img = create_context_image(display_img, context_table_boxes, context_image_boxes,
                                                 context_column_boxes, context_header_boxes, context_footer_boxes)

                print(f"\n✏️ Editing Column {box_index+1}...")
                corrected_boxes = interactive_editor(context_img, [column_coords_display[box_index]], f"Column {box_index+1} Editor")

                if corrected_boxes and len(corrected_boxes) > 0:
                    new_display_boxes = []
                    new_xywh_boxes = []
                    for cb in corrected_boxes:
                        new_display_boxes.append(cb)
                        new_xywh_boxes.append([int(v / scale) for v in cb])

                    column_coords_display.pop(box_index)
                    column_coords_xywh.pop(box_index)
                    column_coords_display.extend(new_display_boxes)
                    column_coords_xywh.extend(new_xywh_boxes)
                else:
                    column_coords_display[box_index] = [0, 0, 0, 0]
                    column_coords_xywh[box_index] = [0, 0, 0, 0]

                save_coords(row_id, filename, table_coords_xywh, image_coords_xywh, column_coords_xywh, header_coords_xywh, footer_coords_xywh)

            # === HEADER EDITING ===
            elif box_type == "header":
                if not (0 <= box_index < len(header_coords_display)):
                    print(f"❌ Header {box_index+1} doesn't exist.")
                    continue

                context_table_boxes = [(box, i) for i, box in enumerate(table_coords_display)]
                context_image_boxes = [(box, i) for i, box in enumerate(image_coords_display)]
                context_column_boxes = [(box, i) for i, box in enumerate(column_coords_display)]
                context_header_boxes = [(box, i) for i, box in enumerate(header_coords_display) if i != box_index]
                context_footer_boxes = [(box, i) for i, box in enumerate(footer_coords_display)]
                context_img = create_context_image(display_img, context_table_boxes, context_image_boxes,
                                                 context_column_boxes, context_header_boxes, context_footer_boxes)

                print(f"\n✏️ Editing Header {box_index+1}...")
                corrected_boxes = interactive_editor(context_img, [header_coords_display[box_index]], f"Header {box_index+1} Editor")

                if corrected_boxes and len(corrected_boxes) > 0:
                    new_display_boxes = []
                    new_xywh_boxes = []
                    for cb in corrected_boxes:
                        new_display_boxes.append(cb)
                        new_xywh_boxes.append([int(v / scale) for v in cb])

                    header_coords_display.pop(box_index)
                    header_coords_xywh.pop(box_index)
                    header_coords_display.extend(new_display_boxes)
                    header_coords_xywh.extend(new_xywh_boxes)
                else:
                    header_coords_display[box_index] = [0, 0, 0, 0]
                    header_coords_xywh[box_index] = [0, 0, 0, 0]

                save_coords(row_id, filename, table_coords_xywh, image_coords_xywh, column_coords_xywh, header_coords_xywh, footer_coords_xywh)

            # === FOOTER EDITING ===
            elif box_type == "footer":
                if not (0 <= box_index < len(footer_coords_display)):
                    print(f"❌ Footer {box_index+1} doesn't exist.")
                    continue

                context_table_boxes = [(box, i) for i, box in enumerate(table_coords_display)]
                context_image_boxes = [(box, i) for i, box in enumerate(image_coords_display)]
                context_column_boxes = [(box, i) for i, box in enumerate(column_coords_display)]
                context_header_boxes = [(box, i) for i, box in enumerate(header_coords_display)]
                context_footer_boxes = [(box, i) for i, box in enumerate(footer_coords_display) if i != box_index]
                context_img = create_context_image(display_img, context_table_boxes, context_image_boxes,
                                                 context_column_boxes, context_header_boxes, context_footer_boxes)

                print(f"\n✏️ Editing Footer {box_index+1}...")
                corrected_boxes = interactive_editor(context_img, [footer_coords_display[box_index]], f"Footer {box_index+1} Editor")

                if corrected_boxes and len(corrected_boxes) > 0:
                    new_display_boxes = []
                    new_xywh_boxes = []
                    for cb in corrected_boxes:
                        new_display_boxes.append(cb)
                        new_xywh_boxes.append([int(v / scale) for v in cb])

                    footer_coords_display.pop(box_index)
                    footer_coords_xywh.pop(box_index)
                    footer_coords_display.extend(new_display_boxes)
                    footer_coords_xywh.extend(new_xywh_boxes)
                else:
                    footer_coords_display[box_index] = [0, 0, 0, 0]
                    footer_coords_xywh[box_index] = [0, 0, 0, 0]

                save_coords(row_id, filename, table_coords_xywh, image_coords_xywh, column_coords_xywh, header_coords_xywh, footer_coords_xywh)

        except Exception as e:
            print(f"❌ Error: {e}")

    # === FINAL SAVE ===
    final_annotated_img = create_annotated_image(original_img, table_coords_xywh, image_coords_xywh,
                                                 column_coords_xywh, header_coords_xywh, footer_coords_xywh)
    bounded_path = os.path.join('bounded_images', f"{row_id}.jpg")
    cv2.imwrite(bounded_path, final_annotated_img)

    print("\n" + "=" * 60)
    print(f"✅ STAGE COMPLETE for {filename} — Final annotated image saved to {bounded_path}")
    print("=" * 60)

def stage_2(
    row_id: str,
    box_type: Optional[str] = None,
    box_index: Optional[int] = None,
    custom_coords: Optional[List[int]] = None
):
    """
    Tests and visualizes a specific bounding box region from an original image.

    This function can be used in two ways:
    1.  **By Index:** Provide `row_id`, `box_type` ('tables' or 'images'), and `box_index`.
    2.  **By Custom Coordinates:** Provide `row_id` and `custom_coords` as [ymin, xmin, ymax, xmax].
    """
    print("=" * 60)
    print("STAGE 2: COORDINATE TESTING")
    print("=" * 60)

    # --- 1. Input Validation ---
    if custom_coords is None and not (box_type and box_index is not None):
        print("❌ Error: You must provide either `custom_coords` or both `box_type` and `box_index`.")
        return

    if box_type and box_type not in ['tables', 'images']:
        print(f"❌ Error: `box_type` must be either 'tables' or 'images', not '{box_type}'.")
        return

    # --- 2. Load Data and Image ---
    coords_path = 'coords.json'
    uploads_dir = 'uploads'

    if not os.path.exists(coords_path):
        print(f"❌ Error: '{coords_path}' not found. Please run stage_1() first.")
        return

    with open(coords_path, 'r') as f:
        all_coords = json.load(f)

    if row_id not in all_coords:
        print(f"❌ Error: `row_id` '{row_id}' not found in '{coords_path}'.")
        return

    # Look up the original filename using the row_id
    original_filename = all_coords[row_id].get("original_filename")
    if not original_filename:
        print(f"❌ Error: 'original_filename' not found for '{row_id}' in coords.json.")
        return

    original_image_path = os.path.join(uploads_dir, original_filename)
    if not os.path.exists(original_image_path):
        print(f"❌ Error: Could not find original image at '{original_image_path}'.")
        return

    original_image = cv2.imread(original_image_path)
    if original_image is None:
        print(f"❌ Error: Failed to load image from '{original_image_path}'.")
        return

    # --- 3. Get Coordinates to Test ---
    coords_to_test = None
    if custom_coords:
        print(f"🧪 Testing custom coordinates for '{row_id}'...")
        if len(custom_coords) != 4:
            print("❌ Error: `custom_coords` must be a list of 4 integers: [ymin, xmin, ymax, xmax].")
            return
        coords_to_test = custom_coords
    else:
        print(f"🧪 Testing '{box_type}' at index {box_index} for '{row_id}'...")
        try:
            boxes_list = all_coords[row_id][box_type]
            coords_to_test = boxes_list[box_index]
        except IndexError:
            box_count = len(all_coords[row_id].get(box_type, []))
            print(f"❌ Error: `box_index` {box_index} is out of bounds. There are only {box_count} boxes for '{box_type}'.")
            return
        except KeyError:
             print(f"❌ Error: `box_type` '{box_type}' not found for '{row_id}'.")
             return

    # --- 4. Check for empty/removed boxes ---
    if coords_to_test == [0,0,0,0] or not coords_to_test:
        print("⚠️ Skipping empty/removed box.")
        return

    # --- 5. Crop and Display ---
    if coords_to_test:
        ymin, xmin, ymax, xmax = map(int, coords_to_test)

        # Ensure coordinates are within image bounds
        h, w, _ = original_image.shape
        ymin, xmin = max(0, ymin), max(0, xmin)
        ymax, xmax = min(h, ymax), min(w, xmax)

        if ymin >= ymax or xmin >= xmax:
            print(f"❌ Error: The coordinates {coords_to_test} result in an empty image region.")
            return

        # Create the side-by-side view
        image_with_box = original_image.copy()
        cv2.rectangle(image_with_box, (xmin, ymin), (xmax, ymax), (255, 0, 255), 3) # Bright magenta box

        print(f"\n📸 Side-by-Side Preview (Original vs. Tested Coordinate):")
        cv2_imshow(np.hstack((original_image, image_with_box)))

        # Also show the zoomed-in crop for detail
        cropped_region = original_image[ymin:ymax, xmin:xmax]
        print(f"\n🖼️  Zoomed-in View of Cropped Region:")
        cv2_imshow(cropped_region)
        print("\n✅ STAGE 2 COMPLETE")
        
def stage_3(
    api_key: Optional[str] = None, 
    custom_system_prompt: Optional[str] = None,
    output_fields: Optional[List[str]] = None,
    exclude_fields: Optional[List[str]] = None,
    model_name: Optional[str] = None,
):
    """
    Processes annotated images through LLM with customizable JSON output.

    Args:
        api_key: Your LLM API key. If None, you will be prompted.
        custom_system_prompt: An optional custom prompt to override the default.
        output_fields: A list of strings specifying which keys to INCLUDE.
                       If None, all fields are included by default.
        exclude_fields: A list of strings specifying which keys to EXCLUDE
                        from the final output. This is applied after `output_fields`.
    """
    print("=" * 60)
    print("STAGE 3: LLM CONTENT EXTRACTION")
    print("=" * 60)

    # --- 1. Determine Final Output Fields ---
    ALL_POSSIBLE_FIELDS = ["Page header", "Page text", "Page footer", "table_bbox", "image_bbox"]
    
    # Start with the user-defined list or all fields
    if output_fields is not None:
        fields_to_include = [field for field in output_fields if field in ALL_POSSIBLE_FIELDS]
    else:
        fields_to_include = ALL_POSSIBLE_FIELDS.copy()

    # Apply exclusions if provided
    if exclude_fields is not None:
        fields_to_include = [field for field in fields_to_include if field not in exclude_fields]
        print(f"✅  Excluding fields: {exclude_fields}")

    print(f"ℹ️  Final JSON will include: {fields_to_include}")

    # Determine model
    chosen_model = model_name or "gemini-1.5-flash"
    print(f"ℹ️  Using model: {chosen_model}")

    # --- 2. Configure Model API ---
    if not api_key:
        try:
            api_key = getpass("🔑 Please enter your Model's API Key: ")
        except Exception as e:
            print(f"Could not read API key: {e}")
            return
            
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"❌ Error configuring API: {e}")
        return

    # --- 3. Define System Prompt ---
    if custom_system_prompt:
        system_prompt = custom_system_prompt
    else:
        system_prompt = r"""
        You are a specialist in Spatial Document Intelligence. Your task is to perform Layout-Aware Content Extraction.
        For each document page, you will analyze its structure, extract all content in the correct reading order, and format the output as a single, clean JSON object.

        **CRITICAL INSTRUCTIONS:**

        1. **Layout Detection & Reading Order:**
            * Accurately identify the layout: `single_column`, `two_column`, `three_column`, or `four_column`.
            * **CRITICAL**: If you see text arranged in distinct vertical columns side-by-side, it is a multi-column layout.
            * **BLUE BOXES** (when present) indicate column boundaries that have been precisely marked for you.
            * **When NO blue boxes are present**: Use visual analysis to detect columns by looking for:
                - Vertical white space separating text blocks
                - Consistent left/right margins creating column boundaries
                - Text that flows top-to-bottom in separate vertical sections
            * For multi-column layouts: Extract the ENTIRE first column (leftmost) from top to bottom, THEN the ENTIRE second column, and so on. DO NOT interleave lines between columns.
            * **MANDATORY**: Complete each column fully before moving to the next column.

        2. **Column-Aware Content Extraction:**
            * **With blue boxes**: Use them as definitive guides for column boundaries and reading order.
            * **Without blue boxes**: Identify column breaks by examining text alignment and vertical spacing.
            * For 2-column layouts: Read left column completely, then right column completely.
            * Ensure ALL visible text content is captured - do not skip any sections.
            * Pay special attention to content that might be in the right margin or right column.

        3. **Header and Footer Extraction:**
            * **ORANGE BOXES** indicate header regions that contain metadata ABOUT the document.
            * **MAGENTA BOXES** indicate footer regions that contain document metadata.
            * **Decision Rule:** Headers and footers contain metadata ABOUT the document, not THE content OF the document.
            * **HEADER Content:** 
                - Document titles/IDs
                - Page numbers (including those in top corners like "1-25")
                - Chapter or section identifiers
            * **FOOTER Content:** Page numbers, footnotes, copyright notices, document-level references.
            * **CRITICAL**: Include ALL text within header boxes, including page numbers in corners.
            * **EXCLUDE from Header/Footer:** Section titles, figure captions, table headers, source citations for specific figures/tables.
            * **CRITICAL**: Source citations that reference specific figures, tables, or content sections belong in "Page text", NOT in footer.
            * Only extract text that falls within the orange (header) and magenta (footer) boxes.
        
        4. **Source Citation Handling:**
            * Source citations for figures/tables (e.g., "SOURCE: I. V. S. Mullis et al., 2001, Mathematics Benchmarking Report...") belong in "Page text".
            * Place source citations immediately after the related content (figure, table, or text section).
            * These citations are content-specific, not document-level metadata.
            * Only document-wide references or copyright notices go in footer.

        5. **Image Placeholder Insertion:**
            * **GREEN BOXES** indicate pre-detected image regions. Your task is to place an `[image]` placeholder in the text where that image logically belongs.
            * Place the `[image]` placeholder at the nearest paragraph break corresponding to its vertical position in the reading order.
            * The image's caption text (e.g., "FIGURE 12. Displacement of pipeline...") must be included in the "Page text" immediately after the `[image]` placeholder, as it appears in the document.
            * The number of `[image]` placeholders MUST match the number of green boxes.

        6. **Mathematical Content (LaTeX Formatting):**
            * **MANDATORY:** All mathematical expressions MUST be in LaTeX format.
            * Use `\[ ... \]` for display equations (equations on their own line).
            * Use `\( ... \)` for inline equations (equations within a line of text).
            * **CRITICAL FOR JSON VALIDITY:** Every backslash `\` in LaTeX commands MUST be escaped with a second backslash. This is required for the output to be valid JSON.
                * **Correct:** `"\\(x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}\\)"`
                * **Incorrect:** `"\(x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}\)"`

        7. **Table Extraction (CRITICAL):**
            * **RED BOXES** indicate pre-detected table regions. Your task is to extract the table content.
            * Extract all tables into clean, standard HTML `<table>` format.
            * Use `<thead>`, `<tbody>`, `<tr>`, `<th>`, and `<td>`.
            * If a header spans multiple rows or columns, explicitly use rowspan or colspan (instead of leaving empty <th> tags).
            * Ensure the number of columns in the header matches the number of data columns.
            * Place the entire `<table>...</table>` string in the "Page text" where it appears in the reading order.

        8. **Content Completeness:**
            * Extract ALL visible text content from the document - do not skip any sections.
            * **CRITICAL**: Check all four edges of the image for text content, especially bottom margins.
            * If text appears to be cut off or incomplete, note this but extract what is visible.
            * Ensure tables are completely extracted with all visible rows and columns.
            * Double-check that content from all columns has been captured.
            * Source citations and references must be included even if they appear in margins.
            * Small or faded text is still important - extract all readable content.

        9. **Edge Content Detection:**
            * Pay special attention to content at the very top and bottom edges of the document.
            * Source citations for figures/tables often appear at bottom margins - these go in "Page text".
            * Look for small text, italicized text, or different formatting that might indicate source material.
            * Common patterns: "SOURCE:", "Note:", author citations, publication references.
            * **IMPORTANT**: Figure/table sources go in "Page text", not footer, even if they appear at document bottom.
            * Document-level footers (page numbers, copyright) go in "Page footer".
            * Scan the entire image area systematically - do not ignore edge regions.

        **VISUAL CUES SUMMARY:**
        * **RED BOXES:** Tables - Extract table content as HTML
        * **GREEN BOXES:** Images - Place `[image]` placeholder + caption in text
        * **BLUE BOXES:** Columns - Define reading order and column boundaries  
        * **CYAN BOXES:** Headers - Extract header metadata
        * **MAGENTA BOXES:** Footers - Extract footer metadata

        **EXTRACTION PRIORITY:**
        1. First, identify headers (cyan boxes) and footers (magenta boxes)
        2. Then, follow column order (blue boxes) for main content
        3. Insert image placeholders (green boxes) at appropriate positions
        4. Extract tables (red boxes) in their reading order position

        **OUTPUT FORMAT (Strictly JSON):**
        Return ONLY a valid JSON object. Do not include any introductory text, explanations, or markdown code fences like ```json.

        {
          "layout_type": "single_column | two_column | three_column | four_column",
          "Page header": "Text from cyan header boxes.",
          "Page text": "All body content from blue column boxes, including [image] placeholders, LaTeX math, and HTML tables, in correct reading order.",
          "Page footer": "Text from magenta footer boxes."
        }
        """
        
    # --- 4. Initialize Model and Load Data ---
    model = genai.GenerativeModel(
        model_name=chosen_model,
        system_instruction=system_prompt
    )
    
    coords_path = 'coords.json'
    bounded_images_dir = 'bounded_images'
    final_outputs_dir = 'final_outputs'
    os.makedirs(final_outputs_dir, exist_ok=True)

    try:
        with open(coords_path, 'r') as f:
            all_coords = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: '{coords_path}' not found. Please run stage_1() first.")
        return

    bounded_images = sorted([f for f in os.listdir(bounded_images_dir) if f.endswith('.jpg')])
    if not bounded_images:
        print(f"❌ Error: No images found in '{bounded_images_dir}/'. Please run stage_1() first.")
        return

    # --- 5. Main Processing Loop ---
    print(f"\n📚 Found {len(bounded_images)} annotated image(s) to process.")
    not_approved_finals = []

    for img_file in bounded_images:
        row_id = os.path.splitext(img_file)[0]
        print("\n" + "=" * 50 + f"\nProcessing: {img_file}\n" + "=" * 50)

        if row_id not in all_coords:
            print(f"⚠️ Warning: No coordinates found for '{row_id}'. Skipping.")
            continue

        try:
            img_path = os.path.join(bounded_images_dir, img_file)
            image_part = {"mime_type": "image/jpeg", "data": open(img_path, 'rb').read()}
            
            print("✨ Extracting content…")
            response = model.generate_content([image_part])
            
            gem_json_str = response.text.strip()
            if gem_json_str.startswith("```json"):
                gem_json_str = gem_json_str[7:-3].strip()
            
            gem_json = json.loads(gem_json_str)
            print("✅ Extraction results ready.")

            # Build the final JSON dynamically based on the final list of fields
            final_json = {}
            for field in fields_to_include:
                if field == "Page header":
                    final_json["Page header"] = gem_json.get("Page header", "")
                elif field == "Page text":
                    final_json["Page text"] = gem_json.get("Page text", "").replace("[image]", "📷")
                elif field == "Page footer":
                    final_json["Page footer"] = gem_json.get("Page footer", "")
                elif field == "table_bbox":
                    final_json["table_bbox"] = all_coords[row_id].get("tables", [])
                elif field == "image_bbox":
                    final_json["image_bbox"] = all_coords[row_id].get("images", [])
            
            print("\n📋 Final JSON for Approval:")
            print("-" * 40)
            print(json.dumps(final_json, indent=2))
            print("-" * 40)

            approval = input("❓ Approve this output? (Enter=Yes, n=No): ").strip().lower()
            if approval == 'n':
                not_approved_finals.append(img_file)
                print("❌ Marked as not approved. Continuing...")
            else:
                output_path = os.path.join(final_outputs_dir, f"{row_id}.json")
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(final_json, f, indent=4, ensure_ascii=False)
                print(f"✅ Approved and saved to: {output_path}")

        except Exception as e:
            print(f"❌ An error occurred while processing {img_file}: {e}")
            not_approved_finals.append(img_file)
            continue
            
    # --- 6. Final Summary ---
    print("\n" + "=" * 60 + "\n✅ STAGE 3 COMPLETE")
    print(f"Total images processed: {len(bounded_images)}")
    approved_count = len(bounded_images) - len(not_approved_finals)
    print(f"  - Approved and saved: {approved_count}")
    print(f"  - Not approved/Failed: {len(not_approved_finals)}")