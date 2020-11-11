## LIBRARIES

# cohort extractor
from cohortextractor import (
    StudyDefinition,
    Measure,
    patients,
    codelist_from_csv,
    codelist,
    filter_codes_by_category,
    combine_codelists
)

## CODELISTS
# All codelist are held within the codelist/ folder.
from codelists import *

# dictionary of STP codes (for dummy data)
from dictionaries import dict_stp


## STUDY POPULATION

index_date = "2020-01-01"

study = StudyDefinition(
        # Configure the expectations framework
    default_expectations={
        "date": {"earliest": index_date, "latest": "today"},
        "rate": "universal",
    },

    index_date = index_date,

    # This line defines the study population
    population = patients.satisfying(
        """
        (sex = 'F' OR sex = 'M') AND
        (age >= 18 AND age < 120) AND
        (NOT died) AND
        (registered)
        """,
        
        died = patients.died_from_any_cause(
		    on_or_before=index_date,
		    returning="binary_flag"
	    ),
        registered = patients.registered_as_of(index_date),
        age=patients.age_as_of(index_date),
        sex=patients.sex(),
    ),

    ### geographic/administrative groups
    practice = patients.registered_practice_as_of(
         index_date,
         returning = "pseudo_id",
         return_expectations={
             "int": {"distribution": "normal", "mean": 100, "stddev": 20}
         },
    ),

    stp = patients.registered_practice_as_of(
        index_date,
        returning="stp_code",
        return_expectations={
            "category": {"ratios": dict_stp},
        },
    ),

    cholesterol = patients.with_these_clinical_events(
        codes_cholesterol,
        returning = "number_of_episodes",
        between = ["index_date", "index_date + 1 month"],
        return_expectations={
            "int": {"distribution": "normal", "mean": 2, "stddev": 0.5}
        },
    ),

    inr = patients.with_these_clinical_events(
        codes_inr,
        returning = "number_of_episodes",
        between = ["index_date", "index_date + 1 month"],
        return_expectations={
            "int": {"distribution": "normal", "mean": 3, "stddev": 0.5}
        },
    ),
)


measures = [
    Measure(
        id="cholesterol_practice",
        numerator="cholesterol",
        denominator="population",
        group_by="practice"
    ),
    Measure(
        id="cholesterol_stp",
        numerator="cholesterol",
        denominator="population",
        group_by="stp"
    ),
    Measure(
        id="inr_practice",
        numerator="inr",
        denominator="population",
        group_by="practice"
    ),
    Measure(
        id="inr_stp",
        numerator="inr",
        denominator="population",
        group_by="stp"
    ),
]

