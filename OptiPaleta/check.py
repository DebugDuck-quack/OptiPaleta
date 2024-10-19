import customtkinter as ctk
from tkinter import messagebox

# Klasa do walidacji danych wejściowych
def validate_box_entry(box_entry):
    try:
        box_data = box_entry.get().split(',')
        if len(box_data) != 6:
            raise ValueError("Nieprawidłowa liczba argumentów.")

        dimensions = list(map(int, box_data[:3]))
        weight = float(box_data[3])
        quantity = int(box_data[4])
        
        # Walidacja danych - wszystkie wartości muszą być dodatnie
        if any(d <= 0 for d in dimensions) or weight <= 0 or quantity <= 0:
            raise ValueError("Wymiary, waga i ilość muszą być dodatnie.")
        
        # Jeśli dane są poprawne, zmień kolor pola na zielony
        box_entry.configure(fg_color="green")
        return True
    except ValueError:
        # Jeśli dane są niepoprawne, zmień kolor pola na czerwony i pokaż błąd
        messagebox.showerror("Błąd", "Wprowadź poprawne dane pudełka w formacie: Dł, Szer, Wys, Waga, Ilość, Blokada osi [opcjonalnie]")
        box_entry.configure(fg_color="red")
        return False

def validate_pallet_entry(pallet_entry, max_weight_entry):
    try:
        pallet_data = pallet_entry.get().split(',')
        pallet_length, pallet_width, pallet_height = map(int, pallet_data)
        max_weight_limit = float(max_weight_entry.get())

        # Jeśli dane są poprawne, zmień kolor pól na zielony
        pallet_entry.configure(fg_color="green")
        max_weight_entry.configure(fg_color="green")
        return True
    except ValueError:
        # Jeśli dane są niepoprawne, zmień kolor pól na czerwony i pokaż błąd
        messagebox.showerror("Błąd", "Wprowadź poprawne dane palety i maksymalne obciążenie")
        pallet_entry.configure(fg_color="red")
        max_weight_entry.configure(fg_color="red")
        return False
