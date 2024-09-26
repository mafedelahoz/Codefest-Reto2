import csv

# Lector de las tablas de encabezado del archivo CSV
def read_csv_header(file_path):
    header_data_1 = {}
    header_data_2 = {}
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            if len(row) == 0 or not row[0]:  
                break
            key_1 = row[0]
            value_1 = row[1] if len(row) > 1 else None
            key_2 = row[4] if len(row) > 4 else None
            value_2 = row[5] if len(row) > 5 else None
            header_data_1[key_1] = value_1
            if key_2:
                header_data_2[key_2] = value_2
    return header_data_1, header_data_2

# Lector de los registros de datos 
def read_csv_data(file_path):
    header_data_1, header_data_2 = read_csv_header(file_path)
    data_records = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        header_processed = False
        for row in reader:
            if not header_processed:
                if len(row) == 0 or not row[0]:
                    header_processed = True
                continue
            cleaned_row = [value for value in row if value]  # Eliminar valores vacíos
            if cleaned_row:  
                data_records.append(cleaned_row)
    return header_data_1, header_data_2, data_records


file_path = 'Dataset_20240914100029.csv'
header_data_1, header_data_2, data_records = read_csv_data(file_path)

print("Tabla 1:")
for key, value in header_data_1.items():
    print(f"{key}: {value}")

print("\nTabla 2:")
for key, value in header_data_2.items():
    print(f"{key}: {value}")

print("\nRegistros de datos:")
for record in data_records:
    print(record)