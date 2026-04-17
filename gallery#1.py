import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading

# ── Theme colours ─────────────────────────────────────────────────────────────
BG          = "#f0f4ff"       # page background
CARD_BG     = "#ffffff"       # card / input background
RED         = "#e63946"       # Pokémon red
RED_DARK    = "#c1121f"       # button hover
DARK        = "#1a1a2e"       # text
MUTED       = "#888888"       # secondary text
BORDER      = "#d0d8f0"       # subtle border

TYPE_COLORS = {
    "fire":     "#FF6B3D", "water":    "#4A9FE0", "grass":    "#5DBD58",
    "electric": "#F5D02E", "psychic":  "#E95693", "ice":      "#78D8D8",
    "dragon":   "#6C4DE1", "dark":     "#594A3A",  "fairy":   "#EE99AC",
    "normal":   "#A8A898", "fighting": "#C03028",  "flying":  "#7BBEFC",
    "poison":   "#A040A0", "ground":   "#E0C068",  "rock":    "#B8A038",
    "bug":      "#A8B820", "ghost":    "#705898",  "steel":   "#B8B8D0",
}

STAT_LABELS = {
    "hp": "HP", "attack": "ATK", "defense": "DEF",
    "special-attack": "Sp.ATK", "special-defense": "Sp.DEF", "speed": "SPD",
}

# ── Data fetcher ──────────────────────────────────────────────────────────────
def fetch_pokemon_data(name: str):
    name = name.strip().lower()
    try:
        poke_res     = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name}", timeout=8)
        poke_res.raise_for_status()
        poke_data    = poke_res.json()

        species_res  = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{name}", timeout=8)
        species_res.raise_for_status()
        species_data = species_res.json()

        desc = next(
            (e["flavor_text"].replace("\n", " ").replace("\f", " ")
             for e in species_data["flavor_text_entries"]
             if e["language"]["name"] == "en"),
            "No description available.",
        )

        return {
            "name":    poke_data["name"].capitalize(),
            "id":      poke_data["id"],
            "types":   [t["type"]["name"] for t in poke_data["types"]],
            "img_url": poke_data["sprites"]["other"]["official-artwork"]["front_default"],
            "desc":    desc,
            "height":  poke_data["height"] / 10,
            "weight":  poke_data["weight"] / 10,
            "stats":   {s["stat"]["name"]: s["base_stat"] for s in poke_data["stats"]},
        }
    except Exception:
        return None

# ── Helper: rounded rectangle on canvas ───────────────────────────────────────
def rounded_rect(canvas, x1, y1, x2, y2, r=10, **kwargs):
    pts = [
        x1+r, y1, x2-r, y1, x2, y1,
        x2, y1+r, x2, y2-r, x2, y2,
        x2-r, y2, x1+r, y2, x1, y2,
        x1, y2-r, x1, y1+r, x1, y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kwargs)

# ── Main window ───────────────────────────────────────────────────────────────
root = tk.Tk()
root.title("Pokémon Gallery")
root.geometry("460x680")
root.resizable(True, True)
root.configure(bg=BG)
root.minsize(400, 600)

# ── Top header bar ────────────────────────────────────────────────────────────
header = tk.Frame(root, bg=RED, pady=14, padx=20)
header.pack(fill=tk.X)

tk.Label(
    header, text="🔴 Pokémon Gallery",
    bg=RED, fg="white",
    font=("Segoe UI", 16, "bold"),
).pack(side=tk.LEFT)

# ── Search row ────────────────────────────────────────────────────────────────
search_frame = tk.Frame(root, bg=BG, pady=16, padx=20)
search_frame.pack(fill=tk.X)

entry_var = tk.StringVar()
entry = tk.Entry(
    search_frame, textvariable=entry_var,
    font=("Segoe UI", 13), relief=tk.FLAT,
    bg=CARD_BG, fg=DARK, insertbackground=DARK,
    bd=0, highlightthickness=2,
    highlightbackground=BORDER, highlightcolor=RED,
)
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 10))
entry.focus()

search_btn = tk.Button(
    search_frame, text="Search",
    font=("Segoe UI", 11, "bold"),
    bg=RED, fg="white", activebackground=RED_DARK, activeforeground="white",
    relief=tk.FLAT, cursor="hand2", padx=18, pady=8,
    bd=0,
)
search_btn.pack(side=tk.RIGHT)

# ── Scrollable content area ───────────────────────────────────────────────────
canvas_frame = tk.Frame(root, bg=BG)
canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

scroll_canvas = tk.Canvas(canvas_frame, bg=BG, bd=0, highlightthickness=0)
scrollbar     = tk.Scrollbar(canvas_frame, orient="vertical", command=scroll_canvas.yview)
scroll_canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

content = tk.Frame(scroll_canvas, bg=BG)
content_window = scroll_canvas.create_window((0, 0), window=content, anchor="nw")

def _on_frame_configure(e):
    scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
content.bind("<Configure>", _on_frame_configure)

def _on_canvas_configure(e):
    scroll_canvas.itemconfig(content_window, width=e.width)
scroll_canvas.bind("<Configure>", _on_canvas_configure)

# Mouse-wheel scroll
def _on_mousewheel(e):
    scroll_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
scroll_canvas.bind_all("<MouseWheel>", _on_mousewheel)

# ── Pokémon card widgets ──────────────────────────────────────────────────────
# These are created once and updated on each search.
card = tk.Frame(content, bg=CARD_BG, bd=0, padx=16, pady=16)

img_label    = tk.Label(card, bg=CARD_BG)
poke_id_lbl  = tk.Label(card, bg=CARD_BG, fg=MUTED,  font=("Segoe UI", 9))
name_lbl     = tk.Label(card, bg=CARD_BG, fg=DARK,   font=("Segoe UI", 18, "bold"))
types_frame  = tk.Frame(card, bg=CARD_BG)
hw_lbl       = tk.Label(card, bg=CARD_BG, fg=MUTED,  font=("Segoe UI", 10))
desc_text    = tk.Text(
    card, wrap=tk.WORD, font=("Segoe UI", 10),
    fg="#555555", bg="#f8faff",
    relief=tk.FLAT, bd=0, padx=10, pady=8,
    state=tk.DISABLED, cursor="arrow",
)
stats_title  = tk.Label(card, bg=CARD_BG, fg=DARK, font=("Segoe UI", 11, "bold"), text="Base Stats")
stats_frame  = tk.Frame(card, bg=CARD_BG)

# ── Status bar ────────────────────────────────────────────────────────────────
status_var = tk.StringVar(value="Enter a Pokémon name and press Search.")
status_bar = tk.Label(
    root, textvariable=status_var,
    bg=DARK, fg="#aaaacc",
    font=("Segoe UI", 9), anchor="w", padx=12, pady=5,
)
status_bar.pack(fill=tk.X, side=tk.BOTTOM)

# ── Stat bar helper ───────────────────────────────────────────────────────────
_stat_rows = []  # keep references to avoid GC

def _build_stat_bar(parent, label: str, value: int):
    row = tk.Frame(parent, bg=CARD_BG)
    row.pack(fill=tk.X, pady=3)

    lbl = tk.Label(row, text=label, width=7, anchor="e",
                   bg=CARD_BG, fg=MUTED, font=("Segoe UI", 9, "bold"))
    lbl.pack(side=tk.LEFT)

    bar_bg = tk.Canvas(row, height=8, bg="#eeeeee", bd=0,
                       highlightthickness=0)
    bar_bg.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 6))

    val_lbl = tk.Label(row, text=str(value), width=3, anchor="w",
                       bg=CARD_BG, fg=DARK, font=("Segoe UI", 9, "bold"))
    val_lbl.pack(side=tk.LEFT)

    _stat_rows.append((bar_bg, value))
    return bar_bg

def _draw_stat_bars(event=None):
    """Draw fill on all stat bars after canvas has a real width."""
    for bar_bg, value in _stat_rows:
        w = bar_bg.winfo_width()
        if w < 2:
            continue
        bar_bg.delete("all")
        fill_w = int(w * min(value / 255, 1.0))
        # background
        bar_bg.create_rectangle(0, 0, w, 8, fill="#eeeeee", outline="")
        # gradient simulation: two-stop via two rectangles
        half = fill_w // 2
        bar_bg.create_rectangle(0, 0, half, 8, fill=RED, outline="")
        bar_bg.create_rectangle(half, 0, fill_w, 8, fill="#457b9d", outline="")

content.bind("<Expose>", _draw_stat_bars)

# ── Type badge helper ─────────────────────────────────────────────────────────
def _show_types(types: list):
    for w in types_frame.winfo_children():
        w.destroy()
    for t in types:
        color = TYPE_COLORS.get(t, "#999999")
        tk.Label(
            types_frame,
            text=t.capitalize(),
            bg=color, fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=10, pady=3,
            relief=tk.FLAT,
        ).pack(side=tk.LEFT, padx=(0, 6))

# ── Populate card ─────────────────────────────────────────────────────────────
def populate_card(result: dict):
    """Fill all card widgets with fetched data and pack the card."""
    global _stat_rows

    # Image
    if result["img_url"]:
        try:
            img_data = requests.get(result["img_url"], timeout=8).content
            img = Image.open(BytesIO(img_data)).resize((200, 200), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            img_label.img = img_tk          # prevent GC
            img_label.config(image=img_tk, text="")
        except Exception:
            img_label.config(image="", text="(no image)")
    else:
        img_label.config(image="", text="(no image)")

    poke_id_lbl.config(text=f"#{result['id']:04d}")
    name_lbl.config(text=result["name"])
    _show_types(result["types"])
    hw_lbl.config(
        text=f"📏 {result['height']:.1f} m   ·   ⚖️ {result['weight']:.1f} kg"
    )

    desc_text.config(state=tk.NORMAL)
    desc_text.delete("1.0", tk.END)
    desc_text.insert(tk.END, result["desc"])
    desc_text.config(state=tk.DISABLED, height=4)

    # Stats
    for w in stats_frame.winfo_children():
        w.destroy()
    _stat_rows = []
    for raw, val in result["stats"].items():
        _build_stat_bar(stats_frame, STAT_LABELS.get(raw, raw), val)

    # Pack card widgets (idempotent)
    card.pack(fill=tk.X, pady=(0, 12))
    img_label.pack(pady=(0, 8))
    poke_id_lbl.pack()
    name_lbl.pack()
    types_frame.pack(pady=(4, 8))
    hw_lbl.pack(pady=(0, 8))
    desc_text.pack(fill=tk.X, padx=4, pady=(0, 12))
    stats_title.pack(anchor="w", pady=(0, 4))
    stats_frame.pack(fill=tk.X)

    # Force layout so bar widths are known before drawing
    root.update_idletasks()
    _draw_stat_bars()

    status_var.set(f"Showing: {result['name']}  (#{result['id']:04d})")

# ── Search logic (threaded to keep UI responsive) ─────────────────────────────
def _do_search():
    name = entry_var.get().strip()
    if not name:
        messagebox.showwarning("Input Error", "Please enter a Pokémon name or number.")
        return

    search_btn.config(state=tk.DISABLED, text="…")
    status_var.set("Fetching Pokémon data…")
    root.update_idletasks()

    def _run():
        result = fetch_pokemon_data(name)
        root.after(0, _on_result, result, name)

    threading.Thread(target=_run, daemon=True).start()

def _on_result(result, query):
    search_btn.config(state=tk.NORMAL, text="Search")
    if result is None:
        status_var.set(f"Not found: '{query}'")
        messagebox.showerror(
            "Not Found",
            f"Could not find data for '{query}'.\nCheck spelling or try a Pokédex number.",
        )
    else:
        populate_card(result)

search_btn.config(command=_do_search)
entry.bind("<Return>", lambda e: _do_search())

root.mainloop()
