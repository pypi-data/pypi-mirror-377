# CHILD MAPPING =================================================================================
MAPPING_CHILD = {
    "cluster_number_child": {
        "name": "V001",
        "dtype": int
    },
    "household_number_child": {
        "name": "V002",
        "dtype": int
    },
    "respondent_line_number_child": {
        "name": "V003",
        "dtype": int
    },
    "index_birth_history": {
        "name": "MIDX",
        "dtype": int
    },
    "birth_order_number": {
        "name": "BORD",
        "dtype": int
    },
    "is_child_alive": {
        "name": "B5",
        "dtype": str
    },
    "gender": {
        "name": "B4",
        "dtype": str
    },
    "dob_cmc": {
        "name": "B3",
        "dtype": int
    },
    "current_age_of_child_in_years": {
        "name": "B8",
        "dtype": int
    },
    "current_age_of_child_in_months": {
        "name": "HW1",
        "dtype": int
    },
    "age_of_child_at_death": {
        "name": "B6",
        "dtype": int,
        "missing": [997, 998, 999]
    },
    "age_of_child_at_death_months_imputed": {
        "name": "B7",
        "dtype": int
    },
    "flag_for_age_of_child_at_death": {
        "name": "B13",
        "dtype": str
    },
    "delivery_place": {
        "name": "M15",
        "dtype": str,
        "missing": [99]
    },
    "delivery_by_caesarean_section": {
        "name": "M17",
        "dtype": str,
        "missing": [9]
    },
    # TODO - SME review is required for this variable
    # "n_antenatal_visits_during_pregnancy": {
    #     "name": "M14",
    #     "dtype": int,
    #     "missing": [98, 99]
    # },
    "size_at_birth": {
        "name": "M18",
        "dtype": str,
        "missing": [8, 9]
    },
    "breastfeeding_duration": {
        "name": "M4",
        "dtype": int,
        "missing": [97, 98, 99]
    }
}

# HOUSEHOLD MAPPING ============================================================================
MAPPING_HOUSEHOLD = {
    "country_code": {
        "name": "HV000",
        "dtype": str
    },
    "cluster_number": {
        "name": "HV001",
        "dtype": int
    },
    "household_number": {
        "name": "HV002",
        "dtype": int
    },
    "household_sample_weight": {
        "name": "HV005",
        "dtype": float
    },
    "interview_month": {
        "name": "HV006",
        "dtype": int
    },
    "interview_year": {
        "name": "HV007",
        "dtype": int
    },
    "interview_day": {
        "name": "HV016",
        "dtype": int
    },
    "place_of_residence": {
        "name": "HV025",
        "dtype": str
    },
    # TODO - SME review is required for this variable
    # "water_source_drinking": {
    #     "name": "HV201",
    #     "dtype": str,
    #     "missing": [99]
    # },
    "time_to_water_source_in_minutes": {
        "name": "HV204",
        "dtype": int,
        "missing": [998, 999],
        "special_recode": {996: 0}  # On premises → 0 minutes
    },
    # TODO - SME review is required for this variable
    # "toilet_facility_type": {
    #     "name": "HV205",
    #     "dtype": str,
    #     "missing": [99]
    # },
    "wealth_index": {
        "name": "HV270",
        "dtype": str
    }
}

# MOTHER MAPPING ===============================================================================
MAPPING_MOTHER = {
    "cluster_number_mother": {
        "name": "V001",
        "dtype": int
    },
    "household_number_mother": {
        "name": "V002",
        "dtype": int
    },
    "respondent_line_number_mother": {
        "name": "V003",
        "dtype": int
    },
    "age_mother": {
        "name": "V012",
        "dtype": int
    },
    "current_marital_status": {
        "name": "V501",
        "dtype": str
    },
    "number_of_other_wives": {
        "name": "V505",
        "dtype": int,
        "missing": [98, 99]
    },
    "education": {
        "name": "V133",
        "dtype": str,
        "missing": [97, 99]
    },
    "educational_attainment": {
        "name": "V149",
        "dtype": str
    },
    "literacy": {
        "name": "V155",
        "dtype": str
    },
    "relationship_to_household_head": {
        "name": "V150",
        "dtype": str
    },
    "n_children_ever_born": {
        "name": "V201",
        "dtype": int
    },
    "currently_working": {
        "name": "V714",
        "dtype": str,
        "missing": [9]
    }
    # TODO - SME review is required for these variables:
    # "age_at_first_birth": {"name": "V212", "dtype": int},
    # "contraceptive_method_current": {"name": "V312", "dtype": str},
    # "contraceptive_use_and_intention": {"name": "V364", "dtype": str},
    # "currently_pregnant": {"name": "V213", "dtype": str},
    # "pregnancy_wanted_current": {"name": "V225", "dtype": str},
    # "child_last_wanted": {"name": "V367", "dtype": str},
}
