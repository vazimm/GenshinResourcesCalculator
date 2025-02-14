import json
import tkinter as tk
from tkinter import ttk
import os

def create_input_window():
    window = tk.Tk()
    window.title("Material Input")
    window.geometry("600x600")
    
    # Canvas e scrollbar
    canvas = tk.Canvas(window)
    scrollbar = ttk.Scrollbar(window, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Dicionários para armazenar os Entry e os Labels de remaining
    entries = {}
    remaining_labels = {}
    
    def update_remaining_labels(remaining_materials):
        for category, items in remaining_labels.items():
            if category in remaining_materials:
                for item, label in items.items():
                    # Procura o item diretamente ou em subcategorias
                    if item in remaining_materials[category]:
                        data = remaining_materials[category][item]
                        if isinstance(data, dict) and "remaining" in data:
                            label.config(text=str(data["remaining"]))
                    else:
                        # Procura entre as subcategorias
                        for subcat, subdata in remaining_materials[category].items():
                            if isinstance(subdata, dict) and item in subdata:
                                if isinstance(subdata[item], dict):
                                    label.config(text=str(subdata[item].get("remaining", "")))
                                else:
                                    label.config(text=str(subdata[item]))
    
    def on_save():
        # Atualiza os valores obtidos a partir dos Entry
        for category, items in entries.items():
            for item_name, entry in items.items():
                try:
                    value = int(entry.get())
                    if category in obtained_materials:
                        if isinstance(obtained_materials[category], dict):
                            if item_name in obtained_materials[category]:
                                obtained_materials[category][item_name] = value
                            else:
                                for subcat, subitems in obtained_materials[category].items():
                                    if isinstance(subitems, dict) and item_name in subitems:
                                        obtained_materials[category][subcat][item_name] = value
                except ValueError:
                    continue
        
        update_obtained_materials(furina_data, obtained_materials)
        remaining_materials = calculate_remaining(furina_data)
        save_to_file(remaining_materials, 'furina_materials.json')
        update_remaining_labels(remaining_materials)
    
    row = 0
    for category, items in furina_data.items():
        ttk.Label(scrollable_frame, text=f"=== {category.upper()} ===").grid(row=row, column=0, columnspan=3, pady=5)
        row += 1
        entries[category] = {}
        remaining_labels[category] = {}
        
        if isinstance(items, dict): 
            for item_name, item_data in items.items():
                if isinstance(item_data, dict):
                    if "required" in item_data:
                        ttk.Label(scrollable_frame, text=f"{item_name}:").grid(row=row, column=0, padx=5)
                        entry = ttk.Entry(scrollable_frame)
                        entry.grid(row=row, column=1, padx=5, pady=2)
                        entries[category][item_name] = entry
                        # Label para quantidade restante
                        remaining = item_data["required"] - item_data["obtained"]
                        rem_label = ttk.Label(scrollable_frame, text=str(remaining))
                        rem_label.grid(row=row, column=2, padx=5)
                        remaining_labels[category][item_name] = rem_label
                        row += 1
                    else:
                        for subitem_name, subitem_data in item_data.items():
                            ttk.Label(scrollable_frame, text=f"{subitem_name}:").grid(row=row, column=0, padx=5)
                            entry = ttk.Entry(scrollable_frame)
                            entry.grid(row=row, column=1, padx=5, pady=2)
                            entries[category][subitem_name] = entry
                            if isinstance(subitem_data, dict) and "required" in subitem_data and "obtained" in subitem_data:
                                remaining = subitem_data["required"] - subitem_data["obtained"]
                            else:
                                remaining = 0
                            rem_label = ttk.Label(scrollable_frame, text=str(remaining))
                            rem_label.grid(row=row, column=2, padx=5)
                            remaining_labels[category][subitem_name] = rem_label
                            row += 1
        else:
            continue
    
    save_button = ttk.Button(scrollable_frame, text="Save", command=on_save)
    save_button.grid(row=row, column=0, columnspan=3, pady=10)
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    scrollable_frame.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    window.mainloop()

# Dados iniciais
furina_data = {
    "name": "Furina",
    "ascension": {
        "varunada_lazurite": {
            "sliver": {"required": 3, "obtained": 0},
            "fragment": {"required": 9, "obtained": 0},
            "chunk": {"required": 9, "obtained": 0},
            "gemstone": {"required": 6, "obtained": 0}
        },
        "nectar": {
            "whopperflower_nectar": {"required": 18, "obtained": 0},
            "shimmering_nectar": {"required": 30, "obtained": 0},
            "energy_nectar": {"required": 36, "obtained": 0}
        },
        "mora": {"required": 420000, "obtained": 0},
        "lakelight_lily": {"required": 168, "obtained": 0},
        "water_failed_transcend": {"required": 46, "obtained": 0}
    },
    "talents": {
        "nectar": {
            "whopperflower_nectar": {"required": 18, "obtained": 0},
            "shimmering_nectar": {"required": 66, "obtained": 0},
            "energy_nectar": {"required": 93, "obtained": 0}
        },
        "mora": {"required": 4957000, "obtained": 0},
        "crown_of_insight": {"required": 3, "obtained": 0},
        "scrolls_of_justice": {
            "philosophies": {"required": 114, "obtained": 0},
            "guide": {"required": 63, "obtained": 0},
            "teachings": {"required": 9, "obtained": 0}
        },
        "boss_items": {
            "lightless_mass": {"required": 18, "obtained": 0}
        }
    }
}

def update_obtained_materials(character, materials):
    for category in materials:
        for item, value in materials[category].items():
            if category in character and item in character[category]:
                character[category][item]["obtained"] = value
            else:
                # Procura em subcategorias
                if category in character and isinstance(character[category], dict):
                    for subcat in character[category]:
                        if isinstance(character[category][subcat], dict) and item in character[category][subcat]:
                            character[category][subcat][item]["obtained"] = value

def calculate_remaining(character):
    remaining = json.loads(json.dumps(character))  # Cópia profunda
    for category in remaining:
        if isinstance(remaining[category], dict):
            for item in remaining[category]:
                if isinstance(remaining[category][item], dict) and "required" in remaining[category][item]:
                    remaining[category][item]["remaining"] = (
                        remaining[category][item]["required"] - 
                        remaining[category][item]["obtained"]
                    )
                else:
                    for subitem in remaining[category][item]:
                        if isinstance(remaining[category][item][subitem], dict) and "required" in remaining[category][item][subitem]:
                            remaining[category][item][subitem]["remaining"] = (
                                remaining[category][item][subitem]["required"] -
                                remaining[category][item][subitem]["obtained"]
                            )
    return remaining

def save_to_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

# Materiais já obtidos iniciais
obtained_materials = {
    "ascension": {
        "varunada_lazurite": {
            "sliver": 0,
            "fragment": 0,
            "chunk": 0,
            "gemstone": 0
        },
        "nectar": {
            "whopperflower_nectar": 0,
            "shimmering_nectar": 0,
            "energy_nectar": 0
        },
        "mora": 0,
        "lakelight_lily": 0,
        "water_failed_transcend": 0
    },
    "talents": {
        "nectar": {
            "whopperflower_nectar": 0,
            "shimmering_nectar": 0,
            "energy_nectar": 0
        },
        "mora": 0,
        "crown_of_insight": 0,
        "scrolls_of_justice": {
            "philosophies": 0,
            "guide": 0,
            "teachings": 0
        },
        "boss_items": {
            "lightless_mass": 0
        }
    }
}

update_obtained_materials(furina_data, obtained_materials)
remaining_materials = calculate_remaining(furina_data)
save_to_file(remaining_materials, 'furina_materials.json')

if __name__ == "__main__":
    # Dados do personagem
    furina_data = {
        "name": "Furina",
        "ascension": {
            "varunada_lazurite": {
                "sliver": {"required": 3, "obtained": 0},
                "fragment": {"required": 9, "obtained": 0},
                "chunk": {"required": 9, "obtained": 0},
                "gemstone": {"required": 6, "obtained": 0}
            },
            "nectar": {
                "whopperflower_nectar": {"required": 18, "obtained": 0},
                "shimmering_nectar": {"required": 30, "obtained": 0},
                "energy_nectar": {"required": 36, "obtained": 0}
            },
            "mora": {"required": 420000, "obtained": 0},
            "lakelight_lily": {"required": 168, "obtained": 0},
            "water_failed_transcend": {"required": 46, "obtained": 0}
        },
        "talents": {
            "nectar": {
                "whopperflower_nectar": {"required": 18, "obtained": 0},
                "shimmering_nectar": {"required": 66, "obtained": 0},
                "energy_nectar": {"required": 93, "obtained": 0}
            },
            "mora": {"required": 4957000, "obtained": 0},
            "crown_of_insight": {"required": 3, "obtained": 0},
            "scrolls_of_justice": {
                "philosophies": {"required": 114, "obtained": 0},
                "guide": {"required": 63, "obtained": 0},
                "teachings": {"required": 9, "obtained": 0}
            },
            "boss_items": {
                "lightless_mass": {"required": 18, "obtained": 0}
            }
        }
    }

    CHARACTER_FILE = 'character.json'
    RESULT_FILE = 'missing_materials.json'

    def initialize_character_file():
        # Cria um arquivo JSON inicialmente com os dados do personagem
        if not os.path.exists(CHARACTER_FILE):
            with open(CHARACTER_FILE, 'w') as f:
                json.dump(furina_data, f, indent=2)
        with open(CHARACTER_FILE, 'r') as f:
            return json.load(f)

    def update_obtained_materials(character, updated_values):
        # Atualiza os valores "obtained" a partir do dicionário updated_values
        for category in updated_values:
            for item, value in updated_values[category].items():
                if category in character and item in character[category]:
                    character[category][item]["obtained"] = value
                else:
                    # Procura em subcategorias
                    if category in character:
                        for subcat in character[category]:
                            if isinstance(character[category][subcat], dict) and item in character[category][subcat]:
                                character[category][subcat][item]["obtained"] = value

    def calculate_remaining(character):
        # Faz uma cópia do objeto e calcula quanto falta de cada material
        remaining = json.loads(json.dumps(character))
        for category in remaining:
            if isinstance(remaining[category], dict):
                for item in remaining[category]:
                    if isinstance(remaining[category][item], dict) and "required" in remaining[category][item]:
                        rem = remaining[category][item]["required"] - remaining[category][item]["obtained"]
                        remaining[category][item]["remaining"] = rem
                    else:
                        for subitem in remaining[category][item]:
                            if isinstance(remaining[category][item][subitem], dict) and "required" in remaining[category][item][subitem]:
                                rem = remaining[category][item][subitem]["required"] - remaining[category][item][subitem]["obtained"]
                                remaining[category][item][subitem]["remaining"] = rem
        return remaining

    def save_to_file(data, filename):
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

    def create_input_window():
        character = initialize_character_file()
        
        window = tk.Tk()
        window.title("Atualização dos Materiais de Furina")
        window.geometry("600x600")
        
        # Configuração do canvas com scrollbar
        canvas = tk.Canvas(window)
        scrollbar = ttk.Scrollbar(window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        entries = {}          # Para capturar o valor inserido
        remaining_labels = {} # Para mostrar o quanto falta
        
        def update_remaining_labels(remaining):
            # Atualiza os labels no display com os valores restantes
            for category in remaining_labels:
                for item in remaining_labels[category]:
                    if category in remaining and item in remaining[category]:
                        data = remaining[category][item]
                        if isinstance(data, dict) and "remaining" in data:
                            remaining_labels[category][item].config(text=str(data["remaining"]))
                    else:
                        # Busca em subcategorias, se necessário
                        for subcat in remaining.get(category, {}):
                            subdata = remaining[category][subcat]
                            if isinstance(subdata, dict) and item in subdata:
                                value = subdata[item].get("remaining", "")
                                remaining_labels[category][item].config(text=str(value))
        
        def on_save():
            updated_values = {}
            # Captura os valores informados pelo usuário e atualiza os dados
            for category in entries:
                updated_values[category] = {}
                for item in entries[category]:
                    try:
                        value = int(entries[category][item].get())
                        updated_values[category][item] = value
                    except ValueError:
                        updated_values[category][item] = 0
            
            # Atualiza os materiais obtidos no objeto do personagem
            update_obtained_materials(character, updated_values)
            # Recalcula os itens restantes
            remaining = calculate_remaining(character)
            # Salva o resultado num novo arquivo JSON
            save_to_file(remaining, RESULT_FILE)
            update_remaining_labels(remaining)
        
        row = 0
        for category in character:
            if category in ["ascension", "talents"]:
                ttk.Label(scrollable_frame, text=f"=== {category.upper()} ===", font=("Helvetica", 12, "bold")).grid(row=row, column=0, columnspan=3, pady=5)
                row += 1
                entries[category] = {}
                remaining_labels[category] = {}
                
                items = character[category]
                for item in items:
                    if isinstance(items[item], dict) and "required" in items[item]:
                        # Material direto
                        ttk.Label(scrollable_frame, text=f"{item}:").grid(row=row, column=0, padx=5)
                        entry = ttk.Entry(scrollable_frame)
                        entry.grid(row=row, column=1, padx=5, pady=2)
                        entries[category][item] = entry
                        
                        rem = items[item]["required"] - items[item]["obtained"]
                        rem_label = ttk.Label(scrollable_frame, text=str(rem))
                        rem_label.grid(row=row, column=2, padx=5)
                        remaining_labels[category][item] = rem_label
                        row += 1
                    elif isinstance(items[item], dict):
                        # Subcategorias ou grupo de itens
                        for subitem in items[item]:
                            ttk.Label(scrollable_frame, text=f"{subitem}:").grid(row=row, column=0, padx=5)
                            entry = ttk.Entry(scrollable_frame)
                            entry.grid(row=row, column=1, padx=5, pady=2)
                            entries[category][subitem] = entry
                            subdata = items[item][subitem]
                            if isinstance(subdata, dict) and "required" in subdata:
                                rem = subdata["required"] - subdata["obtained"]
                            else:
                                rem = 0
                            rem_label = ttk.Label(scrollable_frame, text=str(rem))
                            rem_label.grid(row=row, column=2, padx=5)
                            remaining_labels[category][subitem] = rem_label
                            row += 1
        
        save_button = ttk.Button(scrollable_frame, text="Salvar Atualização", command=on_save)
        save_button.grid(row=row, column=0, columnspan=3, pady=10)
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        window.mainloop()

    if __name__ == "__main__":
        create_input_window()
