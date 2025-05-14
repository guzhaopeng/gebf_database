-- Drop existing tables
DROP TABLE IF EXISTS calculation_subsystem CASCADE;
DROP TABLE IF EXISTS calculation_keyword CASCADE;
DROP TABLE IF EXISTS method_references CASCADE;
DROP TABLE IF EXISTS keywords CASCADE;
DROP TABLE IF EXISTS calculations CASCADE;
DROP TABLE IF EXISTS subsystems CASCADE;
DROP TABLE IF EXISTS systems CASCADE;
DROP TABLE IF EXISTS gebf_methods CASCADE;

-- Table for GEBF methods
CREATE TABLE gebf_methods (
    method_id INTEGER PRIMARY KEY,
    method_name VARCHAR(50) NOT NULL,
    energy_formula TEXT,
    gradient_formula TEXT,
    property_formula TEXT,
    supported_qc_methods TEXT,
    software_dependency VARCHAR(100),
    lsqc_version VARCHAR(10)
);

-- Table for molecular systems
CREATE TABLE systems (
    system_id INTEGER PRIMARY KEY,
    system_name VARCHAR(100) NOT NULL,
    system_type VARCHAR(50),
    geometry_path TEXT,
    atom_count INTEGER,
    charge INTEGER,
    spin_multiplicity INTEGER
);

-- Table for subsystems
CREATE TABLE subsystems (
    subsystem_id INTEGER PRIMARY KEY,
    method_id INTEGER,
    system_id INTEGER,
    subsystem_type VARCHAR(20),
    fragmentation_method VARCHAR(20),
    fragmentation_parameters TEXT,
    fragment_details_path TEXT,
    parent_subsystem_id INTEGER,
    charge INTEGER,
    spin_multiplicity INTEGER,
    energy FLOAT,
    linear_combination_coeff FLOAT,
    background_charge_path TEXT,
    FOREIGN KEY (method_id) REFERENCES gebf_methods(method_id),
    FOREIGN KEY (system_id) REFERENCES systems(system_id),
    FOREIGN KEY (parent_subsystem_id) REFERENCES subsystems(subsystem_id)
);

-- Table for calculations
CREATE TABLE calculations (
    calculation_id INTEGER PRIMARY KEY,
    method_id INTEGER,
    system_id INTEGER,
    calculation_type VARCHAR(50),
    qc_method VARCHAR(50),
    basis_set VARCHAR(50),
    input_file_path TEXT,
    output_file_path TEXT,
    total_energy FLOAT,
    gradient_path TEXT,
    properties TEXT,
    calculation_status VARCHAR(20),
    creation_time TIMESTAMP,
    FOREIGN KEY (method_id) REFERENCES gebf_methods(method_id),
    FOREIGN KEY (system_id) REFERENCES systems(system_id)
);

-- Table for keywords
CREATE TABLE keywords (
    keyword_id INTEGER PRIMARY KEY,
    method_id INTEGER,
    keyword_name VARCHAR(50) NOT NULL,
    default_value VARCHAR(50),
    allowed_values TEXT,
    FOREIGN KEY (method_id) REFERENCES gebf_methods(method_id)
);

-- Table for calculation-keyword associations
CREATE TABLE calculation_keyword (
    calculation_id INTEGER,
    keyword_id INTEGER,
    keyword_value VARCHAR(50),
    PRIMARY KEY (calculation_id, keyword_id),
    FOREIGN KEY (calculation_id) REFERENCES calculations(calculation_id),
    FOREIGN KEY (keyword_id) REFERENCES keywords(keyword_id)
);

-- Table for method references
CREATE TABLE method_references (
    reference_id INTEGER PRIMARY KEY,
    method_id INTEGER,
    reference_content TEXT NOT NULL,
    publication_year INTEGER,
    FOREIGN KEY (method_id) REFERENCES gebf_methods(method_id)
);

-- Table for calculation-subsystem associations
CREATE TABLE calculation_subsystem (
    calculation_id INTEGER,
    subsystem_id INTEGER,
    PRIMARY KEY (calculation_id, subsystem_id),
    FOREIGN KEY (calculation_id) REFERENCES calculations(calculation_id),
    FOREIGN KEY (subsystem_id) REFERENCES subsystems(subsystem_id)
);

-- Indexes for performance
CREATE INDEX idx_system_id ON subsystems(system_id);
CREATE INDEX idx_calc_system_id ON calculations(system_id);
CREATE INDEX idx_calc_type ON calculations(calculation_type);

-- Constraint for calculation_type
ALTER TABLE calculations ADD CONSTRAINT chk_calc_type CHECK (
    calculation_type IN ('SinglePoint', 'GeometryOptimization', 'Frequency', 'NMR', 'LocalizedExcitedState')
);