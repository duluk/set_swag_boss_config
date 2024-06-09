# Note this script was generated by ChatGPT-4. I gave the prompts and the data,
# making refinement requests as the tool was built and GPT-4 did the rest. It's
# quite impressive actually. I have no experience creating GUI applications or
# using Tkinter.

import tkinter as tk
from   tkinter import filedialog, messagebox, ttk
import json
import os
import shutil
from   datetime import datetime

class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def show_tip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, _, _, = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 20
        y = y + self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                      background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def create_tooltip(widget, text):
    tool_tip = ToolTip(widget)
    def enter(event):
        tool_tip.show_tip(text)
    def leave(event):
        tool_tip.hide_tip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


class BossConfigApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SWAG bossConfig.json Configurator")
        self.config_data = None
        self.config_file_path = ""
        self.backup_path = ""

        # Predefined valid bosses and maps
        self.valid_bosses = [
            "gluhar", "goons", "kaban", "killa", "kolontay", 
            "reshala", "sanitar", "shturman", "tagilla", "zryachiy"
        ]
        self.valid_maps = [
            "customs", "factory", "factory_night", "groundzero", "interchange", 
            "laboratory", "lighthouse", "reserve", "shoreline", "streets", "woods"
        ]
        self.map_options = self.valid_maps + ["all"]

        # Default configuration
        self.defaults = {
            "Bosses": {
                "useGlobalBossSpawnChance": True,
                "gluhar": {"reserve": 35},
                "goons": {"customs": 35, "lighthouse": 30, "shoreline": 35, "woods": 35},
                "kaban": {"streets": 35},
                "killa": {"interchange": 35},
                "kolontay": {"groundzero": 35, "streets": 35},
                "reshala": {"customs": 35},
                "sanitar": {"shoreline": 25},
                "shturman": {"woods": 15},
                "tagilla": {"factory": 35, "factory_night": 35},
                "zryachiy": {"lighthouse": 100}
            }
        }
        # Initialize map chances to default settings
        self.fill_default_map_chances()

        # Configure grid layout
        self.root.grid_rowconfigure(5, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # File selection
        self.config_file = tk.StringVar()
        self.file_label = tk.Label(root, text="Configuration File:")
        self.file_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.file_entry = tk.Entry(root, textvariable=self.config_file, width=50)
        self.file_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.browse_button = tk.Button(root, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10, sticky="w")

        # Set Global Boss Spawn Chance
        self.set_global_button = tk.Button(root, text="Set Global Boss Spawn Chance to True", command=self.set_global_spawn_chance_true)
        self.set_global_button.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        create_tooltip(self.set_global_button, "In order for the values in this file to be used, this setting must be set to true")
        self.update_global_button_color()


#################################

#        # Widgets for setting chances for all bosses on a map
#        ttk.Label(root, text="Set All Bosses for Map:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
#        map_combo = ttk.Combobox(root, values=self.valid_maps, width=20)
#        map_combo.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
#        chance_entry = tk.Entry(root, width=10)
#        chance_entry.grid(row=2, column=2, padx=10, pady=10, sticky="ew")
#        ttk.Button(root, text="Set Chance", command=lambda: self.set_all_bosses(map_combo.get(), chance_entry.get())).grid(row=2, column=3, padx=10, pady=10)
#
#        # Widgets for setting chance for a specific boss and map
#        ttk.Label(root, text="Set Chance for Boss and Map:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
#        boss_combo = ttk.Combobox(root, values=self.valid_bosses, width=20)
#        boss_combo.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
#        map_specific_combo = ttk.Combobox(root, values=self.valid_maps, width=20)
#        map_specific_combo.grid(row=3, column=2, padx=10, pady=10, sticky="ew")
#        specific_chance_entry = tk.Entry(root, width=10)
#        specific_chance_entry.grid(row=3, column=3, padx=10, pady=10)
#        ttk.Button(root, text="Set Chance", command=lambda: self.set_specific_boss(boss_combo.get(), map_specific_combo.get(), specific_chance_entry.get())).grid(row=3, column=4, padx=10, pady=10)

#################################

# TODO: incorporate this perhaps, with more labels for boxes
#        # Combobox for selecting a map
#        ttk.Label(root, text="Select Map for All Bosses:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
#        self.map_combo = ttk.Combobox(root, values=["customs", "factory", "woods"], width=20)
#        self.map_combo.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
#
#        # Entry for entering the chance for all bosses
#        ttk.Label(root, text="Chance for All Bosses:").grid(row=0, column=2, padx=10, pady=10, sticky="w")
#        self.all_bosses_chance_entry = tk.Entry(root, width=10)
#        self.all_bosses_chance_entry.grid(row=0, column=3, padx=10, pady=10)
#
#        # Combobox for selecting a specific boss
#        ttk.Label(root, text="Select Boss:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
#        self.boss_combo = ttk.Combobox(root, values=["Boss1", "Boss2", "Boss3"], width=20)
#        self.boss_combo.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
#
#        # Combobox for selecting a map for a specific boss
#        ttk.Label(root, text="Select Map for Boss:").grid(row=1, column=2, padx=10, pady=10, sticky="w")
#        self.map_specific_combo = ttk.Combobox(root, values=["customs", "factory", "woods"], width=20)
#        self.map_specific_combo.grid(row=1, column=3, padx=10, pady=10, sticky="ew")
#
#        # Entry for entering the chance for a specific boss
#        ttk.Label(root, text="Chance for Boss:").grid(row=1, column=4, padx=10, pady=10, sticky="w")
#        self.chance_entry = tk.Entry(root, width=10)
#        self.chance_entry.grid(row=1, column=5, padx=10, pady=10)

#################################

        # Set All Bosses for Map
        self.modify_label = tk.Label(root, text="Set All Bosses for Map:")
        self.modify_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.map_entry = ttk.Combobox(root, values=self.map_options, width=20)
        self.map_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        self.all_bosses_chance_entry = tk.Entry(root, width=10)
        self.all_bosses_chance_entry.grid(row=2, column=2, padx=10, pady=10, sticky="ew")
        self.set_all_bosses_chance_button = tk.Button(root, text="Set Chance for All Bosses", command=self.set_chance_for_all_bosses)
        self.set_all_bosses_chance_button.grid(row=2, column=3, padx=10, pady=10, sticky="w")
        create_tooltip(self.modify_label, "For the selected map, set all bosses to the specified spawn chance. If 'all' is selected, then of course all bosses on all maps will be set that chance")

        # Set Chance for Boss and Map
        self.set_chance_label = tk.Label(root, text="Set Chance for Boss and Map:")
        self.set_chance_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.boss_entry = ttk.Combobox(root, values=self.valid_bosses, width=20)
        self.boss_entry.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        self.map_for_chance_entry = ttk.Combobox(root, values=self.valid_maps, width=20)
        self.map_for_chance_entry.grid(row=3, column=2, padx=10, pady=10, sticky="ew")
        self.chance_entry = tk.Entry(root, width=5)
        self.chance_entry.grid(row=3, column=3, padx=10, pady=10, sticky="ew")
        self.set_chance_button = tk.Button(root, text="Set Chance", command=self.set_chance)
        self.set_chance_button.grid(row=3, column=4, padx=10, pady=10, sticky="w")
        create_tooltip(self.set_chance_label, "For the selected boss on the selected map, set the spawn chance to the specified amount")

        # Set Existing Chances
        self.set_existing_chances_label = tk.Label(root, text="Set Existing Chances to:")
        self.set_existing_chances_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.existing_chance_entry = tk.Entry(root, width=5)
        self.existing_chance_entry.grid(row=4, column=1, padx=10, pady=10, sticky="ew")
        self.set_existing_chances_button = tk.Button(root, text="Set Existing Chances", command=self.set_existing_chances)
        self.set_existing_chances_button.grid(row=4, column=2, padx=10, pady=10, sticky="w")
        create_tooltip(self.set_existing_chances_label, "For any maps that have an existing spawn chance (non-zero), change it to this number")

        # Output Text Box
        self.output_text = tk.Text(root, height=15, width=80)
        self.output_text.grid(row=5, column=0, columnspan=5, padx=10, pady=10, sticky="nsew")

        # Save Changes button
        self.save_button = tk.Button(root, text="Save Changes", command=self.save_changes)
        self.save_button.grid(row=6, column=1, padx=10, pady=10, sticky="ew")
        create_tooltip(self.save_button, "Write the changes to file. Any maps not shown will be set to 0. A backup will be created in the same directory as the config file.")

        # Default button
        self.defaults_button = tk.Button(root, text="Defaults", command=self.load_defaults)
        self.defaults_button.grid(row=6, column=0, padx=10, pady=10, sticky="ew")
        create_tooltip(self.defaults_button, "Restore map spawn settings to the SWAG default (at least at the time of this coding)")

    def fill_default_map_chances(self):
        """ Ensures every boss has all maps defined, defaulting to 0 where not specified. """
        for boss in self.defaults['Bosses']:
            if boss != "useGlobalBossSpawnChance":  # Skip this key as it's not a boss
                for map_name in self.valid_maps:
                    if map_name not in self.defaults['Bosses'][boss]:
                        self.defaults['Bosses'][boss][map_name] = 0  # Set default chance to 0

    def update_global_button_color(self):
        if self.config_data:
            if not self.config_data["Bosses"].get("useGlobalBossSpawnChance", False):
                self.set_global_button.configure(bg='yellow')
            else:
                self.set_global_button.configure(bg='SystemButtonFace')

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            self.config_file.set(filename)
            self.config_file_path = filename
            self.backup_path = os.path.join(os.path.dirname(filename), "backups")
            if not os.path.exists(self.backup_path):
                os.makedirs(self.backup_path)
            self.load_config_data()
            self.update_global_button_color()

    def backup_config(self):
        if self.config_file_path:
            base_name = os.path.basename(self.config_file_path)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            backup_file = f"{base_name}.{timestamp}.bak"
            shutil.copy(self.config_file_path, os.path.join(self.backup_path, backup_file))
            # Clean up old backups, keep only the last 10
            backups = sorted([f for f in os.listdir(self.backup_path) if f.startswith(base_name)],
                             reverse=True)
            for old_backup in backups[10:]:
                os.remove(os.path.join(self.backup_path, old_backup))

    def load_defaults(self):
        self.config_data = json.loads(json.dumps(self.defaults))  # Deep copy defaults to config_data
        self.list_boss_chances()  # Update output box
        messagebox.showinfo("Reset to Defaults", "Configuration has been reset to default settings.")

    def load_config_data(self):
        try:
            with open(self.config_file.get(), 'r') as file:
                self.config_data = json.load(file)
            self.list_boss_chances()  # Automatically display the boss chances
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration file: {e}")

    def set_global_spawn_chance_true(self):
        if self.config_data:
            self.config_data['Bosses']['useGlobalBossSpawnChance'] = True
            self.list_boss_chances()  # Update the output box
            self.update_global_button_color()
        else:
            messagebox.showerror("Error", "No configuration data loaded.")

    def set_chance_for_all_bosses(self):

        if self.config_data:
            map_name = self.map_entry.get()
            chance = int(self.all_bosses_chance_entry.get())
    
            # Validate the input chance
            if not 0 <= chance <= 100:
                messagebox.showerror("Invalid Input", "Please enter a valid chance from 0 to 100.")
                return
            # If valid, process setting the chance
            #print(f"Setting chance for all bosses on map {map_name} to {chance}%")

            if map_name == "all":
                for boss in self.config_data['Bosses']:
                    if isinstance(self.config_data['Bosses'][boss], dict):
                        for valid_map in self.valid_maps:
                            if valid_map != "all" and valid_map in self.config_data['Bosses'][boss]:
                                self.config_data['Bosses'][boss][valid_map] = chance
            else:
                for boss in self.config_data['Bosses']:
                    if isinstance(self.config_data['Bosses'][boss], dict) and map_name in self.config_data['Bosses'][boss]:
                        self.config_data['Bosses'][boss][map_name] = chance
            self.list_boss_chances()  # Update the output box
        else:
            messagebox.showerror("Error", "No configuration data loaded.")

        self.map_entry.set('')
        self.all_bosses_chance_entry.delete(0, tk.END)

#    def modify_allbosses(self):
#        if self.config_data:
#            map_name = self.map_entry.get()
#            if map_name == "all":
#                for boss in self.config_data['Bosses']:
#                    if isinstance(self.config_data['Bosses'][boss], dict):
#                        for valid_map in self.valid_maps:
#                            if valid_map != "all" and valid_map in self.config_data['Bosses'][boss]:
#                                self.config_data['Bosses'][boss][valid_map] = 100
#            else:
#                for boss in self.config_data['Bosses']:
#                    if isinstance(self.config_data['Bosses'][boss], dict) and map_name in self.config_data['Bosses'][boss]:
#                        self.config_data['Bosses'][boss][map_name] = 100
#            self.list_boss_chances()  # Update the output box
#        else:
#            messagebox.showerror("Error", "No configuration data loaded.")
#
#        self.map_entry.set('')

    def set_chance(self):
        if self.config_data:
            boss = self.boss_entry.get()
            map_name = self.map_for_chance_entry.get()
            try:
                chance = int(self.chance_entry.get())
                # Validate the input chance
                if not 0 <= chance <= 100:
                    messagebox.showerror("Invalid Input", "Please enter a valid chance from 0 to 100.")
                    return

                if boss in self.config_data['Bosses'] and map_name in self.config_data['Bosses'][boss]:
                    self.config_data['Bosses'][boss][map_name] = chance
                    self.list_boss_chances()  # Update the output box
                else:
                    messagebox.showerror("Error", f"Invalid boss or map: {boss}, {map_name}")
            except ValueError:
                messagebox.showerror("Error", "Chance must be an integer.")
        else:
            messagebox.showerror("Error", "No configuration data loaded.")

        self.boss_entry.set('')
        self.map_for_chance_entry.set('')
        self.chance_entry.delete(0, tk.END)

    def set_existing_chances(self):
        if self.config_data:
            try:
                new_chance = int(self.existing_chance_entry.get())
                # Validate the input chance
                if not new_chance.isdigit() or not 0 <= new_chance <= 100:
                    messagebox.showerror("Invalid Input", "Please enter a valid chance from 0 to 100.")
                    return

                for boss, maps in self.config_data['Bosses'].items():
                    if isinstance(maps, dict):
                        for map_name in maps:
                            if maps[map_name] != 0:
                                maps[map_name] = new_chance
                self.list_boss_chances()  # Update the output box
            except ValueError:
                messagebox.showerror("Error", "Chance must be an integer.")
        else:
            messagebox.showerror("Error", "No configuration data loaded.")

        self.existing_chance_entry.delete(0, tk.END)

    def list_boss_chances(self):
        if self.config_data:
            output = ""
            for boss, maps in self.config_data['Bosses'].items():
                if isinstance(maps, dict):
                    non_zero_chances = {k: v for k, v in maps.items() if v != 0}
                    if non_zero_chances:
                        output += f"{boss}:\n"
                        for map_name, chance in non_zero_chances.items():
                            output += f"  {map_name}: {chance}\n"
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, output)
        else:
            messagebox.showerror("Error", "No configuration data loaded.")

    def save_changes(self):
        self.backup_config()  # Backup before saving
        if self.config_data:
            try:
                with open(self.config_file_path, 'w') as file:
                    json.dump(self.config_data, file, indent=4)
                messagebox.showinfo("Success", "Changes saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save changes: {e}")
        else:
            messagebox.showerror("Error", "No configuration data loaded.")

# Main
if __name__ == "__main__":
    root = tk.Tk()
    app = BossConfigApp(root)
    root.mainloop()
