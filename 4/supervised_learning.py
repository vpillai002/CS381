from dataclasses import dataclass # For creating classes to store data
from itertools import permutations
from time import process_time
from typing import Optional
import ast


def run_cli():
    while True:
        print("1. Show algorithm summary")
        print("2. Classify an instance")
        print("3. Exit")

        choice = input("Choose an option: ")

        if choice == 1:
             print("Summary is not implemented yet")
        elif choice == "2":
            print("Instance classification is not implemented yet.")
        elif choice == "3":
            break
        else:
            print("Please choose 1, 2, or 3.")
        

if __name__ == "__main__":
        run_cli()
