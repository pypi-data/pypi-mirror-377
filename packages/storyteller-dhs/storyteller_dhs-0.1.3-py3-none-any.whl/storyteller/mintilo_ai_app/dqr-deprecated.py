# Data Quality Rules for Child-related variables
DQ_RULES_CHILD = {
    'age_at_death': [199, 299, 399, 997, 998, 999],
    'child_lives_with_whom': [9],
    'weight_kg': [9994, 9995, 9999, 9996],
    'height_cm': [9994, 9995, 9999, 9996],
    'delivery_place': [99],
    'delivery_by_caesarean_section': [9],
    'n_antenatal_visits_during_pregnancy': [98, 99],
    'size_at_birth': [8, 9],
    'breastfeeding_duration': [97, 98, 99],
    'dob_day': [97, 98, 99]
}

# Data Quality Rules for Household-related variables
DQ_RULES_HOUSEHOLD = {
    'altitude_cluster_in_meters': [9999],
    'toilet_facility_type': [99],
    'gender_household_head': [9],
    'age_household_head': [98, 99],
    'water_source_drinking': [99],
    'time_to_water_source_in_minutes': [998, 999],
    'cooking_fuel_type': [99],
    'material_main_floor': [99],
    'material_main_wall': [99],
    'material_main_roof': [99],
    'is_usual_resident_de_jure': [9],
    'has_slept_last_night_de_facto': [9]
}

# Data Quality Rules for Mother-related variables
DQ_RULES_MOTHER = {
    'current_marital_status': [9],
    'education': [97, 99],
    'educational_attainment': [9],
    'literacy': [9],
    'relationship_to_household_head': [98, 99],
    'contraceptive_method_current': [99],
    'pregnancy_wanted_current': [9],
    'child_last_wanted': [9],
    'currently_working': [9]
}
