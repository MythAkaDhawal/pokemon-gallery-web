import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO

def fetch_pokemon_data(name):
    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
    species_url = f"https://pokeapi.co/api/v2/pokemon-species/{name.lower()}"
    try:
        poke_res = requests.get(url)
        poke_res.raise_for_status()
        poke_data = poke_res.json()

        species_res = requests.get(species_url)
        species_res.raise_for_status()
        species_data = species_res.json()

        # Get English description
        desc = ""
        for entry in species_data["flavor_text_entries"]:
            if entry["language"]["name"] == "en":
                desc = entry["flavor_text"].replace('\n', ' ').replace('\f', ' ')
                break

        types = [t["type"]["name"].capitalize() for t in poke_data["types"]]
        img_url = poke_data["sprites"]["other"]["official-artwork"]["front_default"]
        return {
            "name": poke_data["name"].capitalize(),
            "types": types,
            "img_url": img_url,
            "description": desc
        }
    except Exception as e:
        return None

def search_pokemon():
    name = entry.get().strip()
    if not name:
        messagebox.showwarning("Input Error", "Please enter a Pokémon name.")
        return
    result = fetch_pokemon_data(name)
    if not result:
        messagebox.showerror("Not Found", f"Could not find data for '{name}'.")
        return

    # Update name and types
    name_var.set(result["name"])
    types_var.set(", ".join(result["types"]))
    desc_text.config(state=tk.NORMAL)
    desc_text.delete(1.0, tk.END)
    desc_text.insert(tk.END, result["description"])
    desc_text.config(state=tk.DISABLED)

    # Update image
    if result["img_url"]:
        img_res = requests.get(result["img_url"])
        img = Image.open(BytesIO(img_res.content)).resize((200, 200))
        img_tk = ImageTk.PhotoImage(img)
        img_label.img = img_tk
        img_label.config(image=img_tk)
    else:
        img_label.config(image='', text="No Image")

# GUI setup
root = tk.Tk()
root.title("Pokémon Search")
root.geometry("400x550")
root.resizable(False, False)

main_frame = ttk.Frame(root, padding=10)
main_frame.pack(fill=tk.BOTH, expand=True)

entry = ttk.Entry(main_frame, font=("Arial", 14))
entry.pack(fill=tk.X, pady=(0, 10))
entry.focus()

search_btn = ttk.Button(main_frame, text="Search", command=search_pokemon)
search_btn.pack(pady=(0, 10))

img_label = ttk.Label(main_frame)
img_label.pack(pady=10)

name_var = tk.StringVar()
types_var = tk.StringVar()

name_label = ttk.Label(main_frame, textvariable=name_var, font=("Arial", 16, "bold"))
name_label.pack(pady=(10, 0))

types_label = ttk.Label(main_frame, textvariable=types_var, font=("Arial", 12))
types_label.pack(pady=(0, 10))

desc_label = ttk.Label(main_frame, text="Description:", font=("Arial", 12, "underline"))
desc_label.pack(anchor="w")

desc_text = tk.Text(main_frame, height=5, wrap=tk.WORD, font=("Arial", 11))
desc_text.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
desc_text.config(state=tk.DISABLED)

root.mainloop()