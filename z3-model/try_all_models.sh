# CS+ECON
    # SCB
python3 validator.py --degree CS+ECON --courses working_cs_econ_scb 
    # AB
python3 validator.py --degree CS+ECON --courses working_cs_econ_scb --degree_type AB

# MATH+CS (only SCB)
python3 validator.py --degree MATH+CS --courses working_math_cs_scb

# APMA+CS
python3 validator.py --degree APMA+CS --courses working_apma_cs_scb

# CompBio
    # SCB
python3 validator.py --degree CompBio --courses working_comp_bio_scb
    # AB
python3 validator.py --degree CompBio --courses working_comp_bio_scb --degree_type AB

# CS (Old)
    # SCB
python3 validator.py --requirement_version Old --courses dhw_old_scb
    # AB
python3 validator.py --requirement_version Old --courses dhw_old_scb --degree_type AB

# CS (New)
    # SCB
python3 validator.py --requirement_version New --courses working_new_scb
    # AB
python3 validator.py --requirement_version New --courses working_new_scb --degree_type AB