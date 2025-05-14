cd C:\gebf-database-optimized
echo # Optimized GEBF Database> README.md
echo This repository contains the database schema for the GEBF module, supporting large molecules and clusters.>> README.md
echo.>> README.md
echo ## Schema>> README.md
echo See [gebf_database_schema_optimized.sql](gebf_database_schema_optimized.sql).>> README.md
echo.>> README.md
echo ## Data Insertion>> README.md
echo Use [insert_large_systems.py](insert_large_systems.py) to insert data, with sample data in [protein_xyz.json](protein_xyz.json).>> README.md
git add README.md
git commit -m "Add README"
git push
