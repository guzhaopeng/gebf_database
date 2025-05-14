import psycopg2
import json
import os

# Database connection
conn = psycopg2.connect(
    dbname="gebf_db",
    user="postgres",
    password="bucm123456",  # 替换为实际密码
    host="localhost",
    port="5433"
)
cursor = conn.cursor()

# Insert into gebf_methods
cursor.execute("""
    INSERT INTO gebf_methods (method_id, method_name, energy_formula, gradient_formula, property_formula, supported_qc_methods, software_dependency, lsqc_version)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (method_id) DO NOTHING
""", (
    1, 'GEBF',
    'E_tot = \sum_m C_m E_m - (\sum_m C_m - 1) \sum_A \sum_B Q_A Q_B / R_AB',
    '\partial E_tot / \partial q_A = \sum_m C_m \partial E_m / \partial q_A',
    '\mu_i = \sum_m C_m \mu_i^(m), \alpha_ij = \sum_m C_m \alpha_ij^(m)',
    'AM1,HF,DFT,B3LYP,MP2,CCSD(T)', 'Gaussian', '3.0'
))

# Insert into method_references
cursor.execute("""
    INSERT INTO method_references (reference_id, method_id, reference_content, publication_year)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (reference_id) DO NOTHING
""", (1, 1, 'W. Li, H. Dong, J. Ma, S. Li. Acc. Chem. Res. 2021, 54, 223-234', 2021))

# Insert into keywords
cursor.execute("""
    INSERT INTO keywords (keyword_id, method_id, keyword_name, default_value, allowed_values)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (keyword_id) DO NOTHING
""", (1, 1, 'FRAGSIZE', '10', 'Positive integer'))
cursor.execute("""
    INSERT INTO keywords (keyword_id, method_id, keyword_name, default_value, allowed_values)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (keyword_id) DO NOTHING
""", (2, 1, 'DISTANCE', '4.0', 'Positive float'))

# Protein XYZ data
system_data = {
    "system_id": 1,
    "system_name": "Protein XYZ",
    "system_type": "Protein",
    "geometry_path": r"C:\data\systems\protein_xyz.pdb",
    "atom_count": 1000,
    "charge": 0,
    "spin_multiplicity": 1
}

subsystems_data = [
    {
        "subsystem_id": i,
        "method_id": 1,
        "system_id": 1,
        "subsystem_type": "Primitive" if i <= 20 else "Derived",
        "fragmentation_method": "Auto",
        "fragmentation_parameters": "FRAGSIZE=50, DISTANCE=4.0",
        "fragment_details_path": f"C:\\data\\subsystems\\protein_sub{i}.xyz",
        "parent_subsystem_id": None if i <= 20 else i - 20,
        "charge": 0,
        "spin_multiplicity": 1,
        "energy": -250.1234 + i * 0.1,
        "linear_combination_coeff": 1.0 if i <= 20 else -0.5,
        "background_charge_path": f"C:\\data\\subsystems\\protein_sub{i}_charges.dat"
    } for i in range(1, 31)
]

calculation_data = {
    "calculation_id": 1,
    "method_id": 1,
    "system_id": 1,
    "calculation_type": "SinglePoint",
    "qc_method": "B3LYP",
    "basis_set": "6-31G*",
    "input_file_path": r"C:\data\calculations\protein.inp",
    "output_file_path": r"C:\data\calculations\protein.out",
    "total_energy": -5000.1234,
    "gradient_path": r"C:\data\calculations\protein_gradient.dat",
    "properties": json.dumps({}),
    "calculation_status": "Completed",
    "creation_time": "2025-05-14 10:05:00"
}

# (H2O)20 cluster data
system_data_water = {
    "system_id": 2,
    "system_name": "(H2O)20",
    "system_type": "Cluster",
    "geometry_path": r"C:\data\systems\water_cluster.xyz",
    "atom_count": 60,
    "charge": 0,
    "spin_multiplicity": 1
}

subsystems_data_water = [
    {
        "subsystem_id": i + 30,
        "method_id": 1,
        "system_id": 2,
        "subsystem_type": "Primitive",
        "fragmentation_method": "Auto",
        "fragmentation_parameters": "FRAGSIZE=10",
        "fragment_details_path": f"C:\\data\\subsystems\\water_sub{i}.xyz",
        "parent_subsystem_id": None,
        "charge": 0,
        "spin_multiplicity": 1,
        "energy": -252.1234 + i * 0.1,
        "linear_combination_coeff": 1.0,
        "background_charge_path": f"C:\\data\\subsystems\\water_sub{i}_charges.dat"
    } for i in range(1, 7)
]

calculation_data_water = {
    "calculation_id": 2,
    "method_id": 1,
    "system_id": 2,
    "calculation_type": "Frequency",
    "qc_method": "B3LYP",
    "basis_set": "6-31G*",
    "input_file_path": r"C:\data\calculations\water.inp",
    "output_file_path": r"C:\data\calculations\water.out",
    "total_energy": -1520.5678,
    "gradient_path": r"C:\data\calculations\water_gradient.dat",
    "properties": json.dumps({"vibrational_frequencies": [100.5, 200.3, 300.7]}),
    "calculation_status": "Completed",
    "creation_time": "2025-05-14 10:10:00"
}

# Check files (optional)
for data in [system_data, system_data_water, calculation_data, calculation_data_water]:
    for key in ["geometry_path", "input_file_path", "output_file_path", "gradient_path"]:
        if key in data and not os.path.exists(data[key]):
            print(f"Warning: File {data[key]} not found")
for sub in subsystems_data + subsystems_data_water:
    for key in ["fragment_details_path", "background_charge_path"]:
        if not os.path.exists(sub[key]):
            print(f"Warning: File {sub[key]} not found")

# Insert data
try:
    # Insert Protein XYZ
    cursor.execute("""
        INSERT INTO systems (system_id, system_name, system_type, geometry_path, atom_count, charge, spin_multiplicity)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        system_data["system_id"], system_data["system_name"], system_data["system_type"],
        system_data["geometry_path"], system_data["atom_count"], system_data["charge"],
        system_data["spin_multiplicity"]
    ))

    cursor.executemany("""
        INSERT INTO subsystems (subsystem_id, method_id, system_id, subsystem_type, fragmentation_method, fragmentation_parameters, fragment_details_path, parent_subsystem_id, charge, spin_multiplicity, energy, linear_combination_coeff, background_charge_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, [
        (
            sub["subsystem_id"], sub["method_id"], sub["system_id"], sub["subsystem_type"],
            sub["fragmentation_method"], sub["fragmentation_parameters"], sub["fragment_details_path"],
            sub["parent_subsystem_id"], sub["charge"], sub["spin_multiplicity"], sub["energy"],
            sub["linear_combination_coeff"], sub["background_charge_path"]
        ) for sub in subsystems_data
    ])

    cursor.execute("""
        INSERT INTO calculations (calculation_id, method_id, system_id, calculation_type, qc_method, basis_set, input_file_path, output_file_path, total_energy, gradient_path, properties, calculation_status, creation_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        calculation_data["calculation_id"], calculation_data["method_id"], calculation_data["system_id"],
        calculation_data["calculation_type"], calculation_data["qc_method"], calculation_data["basis_set"],
        calculation_data["input_file_path"], calculation_data["output_file_path"], calculation_data["total_energy"],
        calculation_data["gradient_path"], calculation_data["properties"], calculation_data["calculation_status"],
        calculation_data["creation_time"]
    ))

    cursor.executemany("""
        INSERT INTO calculation_subsystem (calculation_id, subsystem_id)
        VALUES (%s, %s)
    """, [(calculation_data["calculation_id"], sub["subsystem_id"]) for sub in subsystems_data])

    cursor.execute("""
        INSERT INTO calculation_keyword (calculation_id, keyword_id, keyword_value)
        VALUES (%s, %s, %s)
    """, (calculation_data["calculation_id"], 1, '50'))
    cursor.execute("""
        INSERT INTO calculation_keyword (calculation_id, keyword_id, keyword_value)
        VALUES (%s, %s, %s)
    """, (calculation_data["calculation_id"], 2, '4.0'))

    # Insert (H2O)20 cluster
    cursor.execute("""
        INSERT INTO systems (system_id, system_name, system_type, geometry_path, atom_count, charge, spin_multiplicity)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        system_data_water["system_id"], system_data_water["system_name"], system_data_water["system_type"],
        system_data_water["geometry_path"], system_data_water["atom_count"], system_data_water["charge"],
        system_data_water["spin_multiplicity"]
    ))

    cursor.executemany("""
        INSERT INTO subsystems (subsystem_id, method_id, system_id, subsystem_type, fragmentation_method, fragmentation_parameters, fragment_details_path, parent_subsystem_id, charge, spin_multiplicity, energy, linear_combination_coeff, background_charge_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, [
        (
            sub["subsystem_id"], sub["method_id"], sub["system_id"], sub["subsystem_type"],
            sub["fragmentation_method"], sub["fragmentation_parameters"], sub["fragment_details_path"],
            sub["parent_subsystem_id"], sub["charge"], sub["spin_multiplicity"], sub["energy"],
            sub["linear_combination_coeff"], sub["background_charge_path"]
        ) for sub in subsystems_data_water
    ])

    cursor.execute("""
        INSERT INTO calculations (calculation_id, method_id, system_id, calculation_type, qc_method, basis_set, input_file_path, output_file_path, total_energy, gradient_path, properties, calculation_status, creation_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        calculation_data_water["calculation_id"], calculation_data_water["method_id"], calculation_data_water["system_id"],
        calculation_data_water["calculation_type"], calculation_data_water["qc_method"], calculation_data_water["basis_set"],
        calculation_data_water["input_file_path"], calculation_data_water["output_file_path"], calculation_data_water["total_energy"],
        calculation_data_water["gradient_path"], calculation_data_water["properties"], calculation_data_water["calculation_status"],
        calculation_data_water["creation_time"]
    ))

    cursor.executemany("""
        INSERT INTO calculation_subsystem (calculation_id, subsystem_id)
        VALUES (%s, %s)
    """, [(calculation_data_water["calculation_id"], sub["subsystem_id"]) for sub in subsystems_data_water])

    cursor.execute("""
        INSERT INTO calculation_keyword (calculation_id, keyword_id, keyword_value)
        VALUES (%s, %s, %s)
    """, (calculation_data_water["calculation_id"], 1, '10'))

    conn.commit()
    print("Data inserted successfully.")
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
finally:
    cursor.close()
    conn.close()