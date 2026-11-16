import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.utils import clear_data

"""czyszczenie tabeli"""

if __name__ == '__main__':
    if input("Wpisz 'tak', aby usunąć wszystkie dane: ") == "tak":
        clear_data()