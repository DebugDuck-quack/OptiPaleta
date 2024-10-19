import pulp
import itertools
from utils import calculate_pallet_height

class Optimization:
    def __init__(self, pallet_dimensions, max_weight_limit, box_list):
        self.pallet_dimensions = pallet_dimensions
        self.max_weight_limit = max_weight_limit
        self.box_list = box_list
        self.total_weight = 0
        self.placed_boxes_count = {}
        self.pallets = []

    def optimize_boxes_with_solver(self):
        # Definicja solvera problemu pakowania
        problem = pulp.LpProblem("Pallet_Optimization", pulp.LpMinimize)
        
        # Ustalamy większą liczbę palet, aby solver miał większą elastyczność
        num_pallets = len(self.box_list) * 2
        pallets = [pulp.LpVariable(f"Pallet_{i}", cat='Binary') for i in range(num_pallets)]
        box_vars = {}

        # Przygotowanie zmiennych dla solvera
        for box in self.box_list:
            box_vars[box['label']] = [pulp.LpVariable(f"Box_{box['label']}_Pallet_{i}", lowBound=0, cat='Integer') for i in range(num_pallets)]
        
        # Definicja funkcji celu: minimalizowanie liczby palet
        problem += pulp.lpSum(pallets)

        # Definicja ograniczeń dla wag, objętości i wysokości palet
        for i in range(num_pallets):
            # Ograniczenie maksymalnej wagi dla każdej palety
            problem += pulp.lpSum([box_vars[box['label']][i] * box['weight'] for box in self.box_list]) <= self.max_weight_limit * pallets[i], f"Weight_Limit_Pallet_{i}"
            
            # Ograniczenie maksymalnej objętości dla każdej palety
            problem += pulp.lpSum([box_vars[box['label']][i] * box['dimensions'][0] * box['dimensions'][1] * box['dimensions'][2] for box in self.box_list]) <= self.pallet_dimensions[0] * self.pallet_dimensions[1] * self.pallet_dimensions[2] * pallets[i], f"Volume_Limit_Pallet_{i}"
            
            # Ograniczenie maksymalnej wysokości dla każdej palety
            problem += pulp.lpSum([box_vars[box['label']][i] * box['dimensions'][2] for box in self.box_list]) <= self.pallet_dimensions[2] * pallets[i], f"Height_Limit_Pallet_{i}"

        # Każde pudełko musi być umieszczone na jednej z palet
        for box in self.box_list:
            problem += pulp.lpSum([box_vars[box['label']][i] for i in range(num_pallets)]) == box['quantity'], f"Box_Placement_{box['label']}"

        # Rozwiązanie problemu
        problem.solve()

        # Zbieranie wyników
        self.pallets = []
        for i in range(num_pallets):
            if pulp.value(pallets[i]) == 1:
                pallet_content = {
                    'pallet_id': f"PALETA nr {i + 1}",
                    'boxes': [],
                    'total_weight': 0
                }
                for box in self.box_list:
                    quantity = int(pulp.value(box_vars[box['label']][i]))
                    if quantity > 0:
                        pallet_content['boxes'].append({'label': box['label'], 'quantity': quantity, 'dimensions': box['dimensions']})
                        pallet_content['total_weight'] += quantity * box['weight']
                self.pallets.append(pallet_content)

        return self.pallets

    def generate_report(self):
        report = """Raport optymalizacji palet:
        Wymiary palety: {}x{}x{} mm
        Maksymalne obciążenie palety: {} kg
        """.format(self.pallet_dimensions[0], self.pallet_dimensions[1], self.pallet_dimensions[2], self.max_weight_limit)
        
        for pallet in self.pallets:
            report += f"\n{pallet['pallet_id']} - Łączna waga: {pallet['total_weight']} kg\n"
            report += f"Wymiary palety po zatowarowaniu pudełkami [mm]: {self.pallet_dimensions[0]}x{self.pallet_dimensions[1]}x{self.calculate_pallet_height(pallet)}\n"
            for box in pallet['boxes']:
                report += f"  Pudełko {box['label']}: {box['quantity']} szt.\n"
        
        # Zapis do pliku txt
        with open('pallet_optimization_report.txt', 'w') as file:
            file.write(report)

        return report

    def calculate_pallet_height(self, pallet):
        # Funkcja do obliczenia wysokości palety po zatowarowaniu pudełkami
        height = 144  # Wysokość palety
        for box in pallet['boxes']:
            height += box['dimensions'][2] * box['quantity']  # Dodanie wysokości pudełek
            if height > self.pallet_dimensions[2]:
                height = self.pallet_dimensions[2]  # nie przekracza limitu
                break
        return height
