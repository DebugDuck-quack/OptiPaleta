import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
import random
import datetime
from optimization import Optimization
from reporting import Reporting
from check import validate_box_entry, validate_pallet_entry

# Klasa aplikacji do optymalizacji rozmieszczenia pudełek na palecie
class BoxOptimizerApp:
    def __init__(self, root):
        # Inicjalizacja głównego okna aplikacji
        self.root = root
        self.root.title("OptiPaleta - Optymalizacja rozmieszczenia pudełek na palecie")

        # Główna ramka aplikacji
        self.frame = ctk.CTkFrame(root, corner_radius=10)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Instrukcja użytkowania (estetyczna forma)
        instructions_text = (
            "1. Wprowadź wymiary palety i maksymalne obciążenie.\n"
            "2. Dodaj pudełko, wpisując jego wymiary, wagę, ilość, oraz blokadę osi (jeśli dotyczy).\n"
            "3. Edytuj lub usuń pudełka, korzystając z odpowiednich przycisków.\n"
            "4. Kliknij 'Solver', aby przeprowadzić optymalizację rozmieszczenia pudełek.\n"
            "5. Po zakończeniu optymalizacji wygeneruj raport.\n"
            "6. Aby zaimportować raport, kliknij 'Importuj raport' i wybierz plik."
        )
        self.instructions_label = ctk.CTkLabel(self.frame, text=instructions_text, justify="left")
        self.instructions_label.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 20), sticky="w")

        # Ustawienia palety - wprowadzenie wymiarów
        self.pallet_label = ctk.CTkLabel(self.frame, text="Wymiary palety [mm] (Dł, Szer, Wys)")
        self.pallet_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.pallet_entry = ctk.CTkEntry(self.frame, placeholder_text="np. 1200, 800, 288", width=250)
        self.pallet_entry.grid(row=1, column=1, padx=10, pady=5)

        # Maksymalne obciążenie palety
        self.max_weight_label = ctk.CTkLabel(self.frame, text="Maksymalne obciążenie palety [kg]")
        self.max_weight_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.max_weight_entry = ctk.CTkEntry(self.frame, placeholder_text="np. 1000", width=250)
        self.max_weight_entry.grid(row=2, column=1, padx=10, pady=5)

        # Dodawanie pudełek
        self.box_label = ctk.CTkLabel(self.frame, text="Dodaj pudełko (Dł, Szer, Wys, Waga, Ilość, Blokada osi)")
        self.box_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        self.box_entry = ctk.CTkEntry(self.frame, placeholder_text="np. 400, 300, 200, 10, 5, 0", width=250)
        self.box_entry.grid(row=3, column=1, padx=10, pady=5)

        self.add_box_button = ctk.CTkButton(self.frame, text="Dodaj pudełko", command=self.add_box)
        self.add_box_button.grid(row=3, column=2, padx=10, pady=5)

        # Lista pudełek
        self.box_list_label = ctk.CTkLabel(self.frame, text="Lista pudełek")
        self.box_list_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        self.box_listbox = tk.Listbox(self.frame, width=60)
        self.box_listbox.grid(row=4, column=1, columnspan=2, padx=10, pady=5)

        # Przycisk usuwania pudełka
        self.delete_box_button = ctk.CTkButton(self.frame, text="Usuń zaznaczone pudełko", command=self.delete_box)
        self.delete_box_button.grid(row=5, column=0, columnspan=3, padx=10, pady=5)

        # Przycisk edytowania pudełka
        self.edit_box_button = ctk.CTkButton(self.frame, text="Edytuj zaznaczone pudełko", command=self.edit_box)
        self.edit_box_button.grid(row=6, column=0, columnspan=3, padx=10, pady=5)

        # Przycisk uruchomienia solvera
        self.solver_button = ctk.CTkButton(self.frame, text="Solver", command=self.solve_optimization)
        self.solver_button.grid(row=7, column=0, columnspan=3, padx=10, pady=20)

        # Przycisk generowania raportu
        self.report_button = ctk.CTkButton(self.frame, text="Generuj raport", command=self.generate_report)
        self.report_button.grid(row=8, column=0, columnspan=3, padx=10, pady=20)

        # Przycisk importowania raportu
        self.import_button = ctk.CTkButton(self.frame, text="Importuj raport", command=self.import_report)
        self.import_button.grid(row=9, column=0, columnspan=3, padx=10, pady=20)

        # Inicjalizacja listy pudełek
        self.box_list = []
        self.pallets = []
        self.total_weight = 0
        self.pallet_dimensions = []
        self.max_weight_limit = 0

    # Dodawanie pudełka do listy
    def add_box(self):
        if validate_box_entry(self.box_entry):
            box_data = self.box_entry.get().split(',')
            dimensions = list(map(int, box_data[:3]))
            weight = float(box_data[3])
            quantity = int(box_data[4])
            axis_lock = box_data[5].strip() if len(box_data) > 5 else '0'
            label = chr(65 + len(self.box_list))
            color = f"#{random.randint(0, 255):02X}{random.randint(0, 255):02X}{random.randint(0, 255):02X}"
            box_info = {'label': label, 'dimensions': dimensions, 'weight': weight, 'quantity': quantity, 'axis_lock': axis_lock, 'color': color}
            self.box_list.append(box_info)
            self.update_box_listbox()
        else:
            messagebox.showerror("Błąd", "Wprowadź poprawne dane pudełka w formacie: Dł, Szer, Wys, Waga, Ilość, Blokada osi.")

    # Edycja zaznaczonego pudełka
    def edit_box(self):
        try:
            selected_index = self.box_listbox.curselection()[0]
            box_to_edit = self.box_list[selected_index]
            edit_window = tk.Toplevel(self.root)
            edit_window.title("Edytuj pudełko")

            # Formularz edycji
            tk.Label(edit_window, text="Wymiary (Dł, Szer, Wys)").grid(row=0, column=0, padx=10, pady=5)
            dimensions_entry = tk.Entry(edit_window)
            dimensions_entry.insert(0, ', '.join(map(str, box_to_edit['dimensions'])))
            dimensions_entry.grid(row=0, column=1, padx=10, pady=5)

            tk.Label(edit_window, text="Waga [kg]").grid(row=1, column=0, padx=10, pady=5)
            weight_entry = tk.Entry(edit_window)
            weight_entry.insert(0, box_to_edit['weight'])
            weight_entry.grid(row=1, column=1, padx=10, pady=5)

            tk.Label(edit_window, text="Ilość").grid(row=2, column=0, padx=10, pady=5)
            quantity_entry = tk.Entry(edit_window)
            quantity_entry.insert(0, box_to_edit['quantity'])
            quantity_entry.grid(row=2, column=1, padx=10, pady=5)

            tk.Label(edit_window, text="Blokada osi [0/x/y/z]").grid(row=3, column=0, padx=10, pady=5)
            axis_lock_entry = tk.Entry(edit_window)
            axis_lock_entry.insert(0, box_to_edit['axis_lock'])
            axis_lock_entry.grid(row=3, column=1, padx=10, pady=5)

            def save_changes():
                try:
                    new_dimensions = list(map(int, dimensions_entry.get().split(',')))
                    new_weight = float(weight_entry.get())
                    new_quantity = int(quantity_entry.get())
                    new_axis_lock = axis_lock_entry.get().strip()

                    # Aktualizacja danych pudełka
                    self.box_list[selected_index]['dimensions'] = new_dimensions
                    self.box_list[selected_index]['weight'] = new_weight
                    self.box_list[selected_index]['quantity'] = new_quantity
                    self.box_list[selected_index]['axis_lock'] = new_axis_lock
                    self.update_box_listbox()
                    edit_window.destroy()
                except ValueError:
                    messagebox.showerror("Błąd", "Wprowadź poprawne dane pudełka.")

            save_button = tk.Button(edit_window, text="Zapisz", command=save_changes)
            save_button.grid(row=4, column=0, columnspan=2, pady=10)
        except IndexError:
            messagebox.showerror("Błąd", "Wybierz pudełko do edycji.")

    # Usuwanie zaznaczonego pudełka z listy
    def delete_box(self):
        try:
            selected_index = self.box_listbox.curselection()[0]
            del self.box_list[selected_index]
            self.update_box_listbox()
        except IndexError:
            messagebox.showerror("Błąd", "Wybierz pudełko do usunięcia.")

    # Aktualizacja widoku listy pudełek
    def update_box_listbox(self):
        self.box_listbox.delete(0, tk.END)
        for box in self.box_list:
            lock_info = f", blokada osi: {box['axis_lock']}" if box['axis_lock'] != '0' else ""
            self.box_listbox.insert(tk.END, f"{box['label']}: {box['dimensions']} - waga: {box['weight']} kg, ilość: {box['quantity']}{lock_info}")
            self.box_listbox.itemconfig(tk.END, {'fg': box['color']})

    # Uruchamianie solvera i optymalizacja
    def solve_optimization(self):
        if not validate_pallet_entry(self.pallet_entry, self.max_weight_entry):
            return

        pallet_data = self.pallet_entry.get().split(',')
        pallet_length, pallet_width, pallet_height = map(int, pallet_data)
        self.pallet_dimensions = [pallet_length, pallet_width, pallet_height - 144]
        self.max_weight_limit = float(self.max_weight_entry.get())

        optimizer = Optimization(self.pallet_dimensions, self.max_weight_limit, self.box_list)
        self.pallets = optimizer.optimize_boxes_with_solver()
        self.total_weight = sum(pallet['total_weight'] for pallet in self.pallets)

        if self.pallets:
            details = [
                f"Optymalizacja zakończona pomyślnie.",
                f"Liczba palet: {len(self.pallets)}",
                f"Łączna waga pudełek: {self.total_weight} kg"
            ]
            for i, pallet in enumerate(self.pallets):
                details.append(f"\nPALETA {i + 1} - Łączna waga: {pallet['total_weight']} kg")
                details.append(f"Wymiary palety po zatowarowaniu pudełkami [mm]: {self.pallet_dimensions[0]}x{self.pallet_dimensions[1]}x{self.calculate_pallet_height(pallet)}")
                for box in pallet['boxes']:
                    details.append(f"  Pudełko {box['label']}: {box['quantity']} szt.")
            messagebox.showinfo("Wyniki optymalizacji", "\n".join(details))
        else:
            messagebox.showwarning("Brak miejsca", "Nie udało się umieścić pudełek na palecie. Zmniejsz liczbę pudełek lub zmień wymiary palety.")

    # Generowanie raportu
    def generate_report(self):
        if not self.pallets:
            messagebox.showerror("Błąd", "Brak danych do generowania raportu.")
            return

        reporter = Reporting(self.box_list, {}, self.total_weight, self.pallet_dimensions, self.pallets, self.max_weight_limit)
        current_time = datetime.datetime.now().strftime("%H-%M_%d-%m-%Y")
        report_filename = f"raport_{current_time}.txt"
        reporter.export_to_txt(report_filename)
        messagebox.showinfo("Raport", f"Raport zapisano jako {report_filename}")

    # Importowanie raportu
    def import_report(self):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not filename:
            return

        try:
            reporter = Reporting(self.box_list, {}, self.total_weight, self.pallet_dimensions, self.pallets, self.max_weight_limit)
            reporter.import_from_txt(filename)

            # Aktualizacja danych po imporcie
            self.box_list = reporter.box_list
            self.pallet_dimensions = reporter.pallet_dimensions
            self.max_weight_limit = reporter.max_weight_limit
            self.update_box_listbox()

            messagebox.showinfo("Import", "Dane zostały zaimportowane z pliku.")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas importu: {e}")

    # Funkcja do obliczenia wysokości palety po zatowarowaniu pudełkami
    def calculate_pallet_height(self, pallet):
        height = 144  # Wysokość palety
        for box in pallet['boxes']:
            height += box['dimensions'][2] * box['quantity']  # Dodanie wysokości pudełek
            if height > self.pallet_dimensions[2]:
                height = self.pallet_dimensions[2]  # Zapewnienie, że wysokość nie przekracza limitu
                break
        return height


