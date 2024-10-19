import matplotlib.pyplot as plt
from utils import calculate_pallet_height
class Reporting:
    def __init__(self, box_list, placed_boxes_count, total_weight, pallet_dimensions, pallets, max_weight_limit):
        self.box_list = box_list
        self.placed_boxes_count = placed_boxes_count
        self.total_weight = total_weight
        self.pallet_dimensions = pallet_dimensions
        self.pallets = pallets
        self.max_weight_limit = max_weight_limit

    def export_to_txt(self, filename='pallet_optimization_report.txt'):
        report = """Raport optymalizacji palet:
        Wprowadzony wymiar palety [mm]: {}x{}x{}
        Maksymalne obciążenie palety [kg]: {}

        LISTA PUDEŁEK:
        """.format(self.pallet_dimensions[0], self.pallet_dimensions[1], self.pallet_dimensions[2], self.max_weight_limit)

        for box in self.box_list:
            dimensions = box.get('dimensions', [0, 0, 0])
            weight = box.get('weight', 0)
            quantity = box.get('quantity', 0)
            axis_lock = box.get('axis_lock', '0')
            label = box.get('label', '?')
            report += f"        Pudełko {label}: {dimensions} - waga: {weight} kg, ilość: {quantity}, blokada osi: {axis_lock if axis_lock != '0' else 'brak'}\n"

        total_weight_on_pallets = sum(pallet['total_weight'] for pallet in self.pallets)
        report += f"\nObciążenie na wszystkich paletach [kg]: {total_weight_on_pallets}\n"

        for pallet in self.pallets:
            report += f"\n{pallet['pallet_id']} - Łączna waga: {pallet['total_weight']} kg\n"
            report += f"Wymiary palety po zatowarowaniu pudełkami [mm]: {self.pallet_dimensions[0]}x{self.pallet_dimensions[1]}x{self.calculate_pallet_height(pallet)}\n"
            for box in pallet['boxes']:
                report += f"  Pudełko {box['label']}: {box['quantity']} szt.\n"

        # DANE DO IMPORTU
        report += "\n-----DANE DO IMPORTU\n"
        report += f"{self.pallet_dimensions[0]},{self.pallet_dimensions[1]},{self.pallet_dimensions[2]}\n"
        report += f"{total_weight_on_pallets}\n"
        for box in self.box_list:
            dimensions = box.get('dimensions', [0, 0, 0])
            weight = box.get('weight', 0)
            quantity = box.get('quantity', 0)
            axis_lock_value = box.get('axis_lock', '0')
            report += f"{dimensions[0]},{dimensions[1]},{dimensions[2]},{weight},{quantity},{axis_lock_value}\n"

        with open(filename, 'w') as file:
            file.write(report)

    def calculate_pallet_height(self, pallet):
        # Funkcja do obliczenia wysokości palety po zatowarowaniu pudełkami
        height = 144  # Wysokość palety
        for box in pallet['boxes']:
            height += box['dimensions'][2] * box['quantity']  # Dodanie wysokości pudełek
            if height > self.pallet_dimensions[2]:
                height = self.pallet_dimensions[2]  # Zapewnienie, że wysokość nie przekracza limitu
                break
        return height

    def import_from_txt(self, filename):
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()
                data_start = lines.index("-----DANE DO IMPORTU\n") + 1
                pallet_dimensions = list(map(int, lines[data_start].strip().split(',')))
                max_weight_limit = float(lines[data_start + 1].strip())
                box_data_lines = lines[data_start + 2:]

                # Aktualizacja wymiarów palety i maksymalnego obciążenia
                self.pallet_dimensions = pallet_dimensions
                self.max_weight_limit = max_weight_limit
                self.box_list = []

                # Dodawanie pudełek
                for line in box_data_lines:
                    if line.strip():
                        dimensions, weight, quantity, axis_lock = line.strip().split(',')[:4], float(line.strip().split(',')[3]), int(line.strip().split(',')[4]), line.strip().split(',')[5]
                        dimensions = list(map(int, dimensions))
                        label = chr(65 + len(self.box_list))
                        box_info = {'label': label, 'dimensions': dimensions, 'weight': weight, 'quantity': quantity, 'axis_lock': axis_lock}
                        self.box_list.append(box_info)
        except Exception as e:
            raise Exception(f"Wystąpił błąd podczas importu: {e}")
