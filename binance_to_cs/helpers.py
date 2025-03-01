
import csv


def write_to_csv(column_names, data):
    with open("output.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(column_names) 
        writer.writerow(data) 