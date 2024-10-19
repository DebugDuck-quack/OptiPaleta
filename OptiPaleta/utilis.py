def calculate_pallet_height(pallet, max_pallet_height=144):
    """
    Funkcja do obliczenia wysokości palety po zatowarowaniu pudełkami.
    :param pallet: Słownik zawierający informacje o palecie, w tym liste pudełek.
    :param max_pallet_height: Maksymalna wysokość palety (domyślnie 144 mm).
    :return: Obliczona wysokość palety.
    """
    height = max_pallet_height  # Poczatkowa wysokość pal
    for box in pallet['boxes']:
        height += box['dimensions'][2] * box['quantity']  # Dodanie wysokości pudełek
        if height > max_pallet_height:
            height = max_pallet_height  # Z limit
            break
    return height