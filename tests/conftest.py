"""Shared pytest fixtures — fake AACT subset for pilot tests."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


def _w(tmp_path: Path, name: str, df: pd.DataFrame) -> None:
    df.to_csv(tmp_path / f"{name}.txt", sep="|", index=False)


@pytest.fixture
def fake_aact(tmp_path: Path) -> Path:
    """Fake AACT snapshot dir with 8 trials (6 malaria, 2 control)."""
    _w(tmp_path, "studies", pd.DataFrame({
        "nct_id": [f"NCT0{i}" for i in range(1, 9)],
        "brief_title": [
            "Artemether-lumefantrine in children with falciparum malaria",
            "RTS,S vaccine efficacy in infants",
            "Artesunate-mefloquine vs DHA-piperaquine",
            "Tafenoquine for vivax radical cure",
            "PfSPZ challenge vaccine in non-immune adults",
            "DHA-piperaquine mass drug administration",
            "Type 2 diabetes glycemic control",
            "Hypertension management",
        ],
        "phase": ["PHASE3", "PHASE3", "PHASE2", "PHASE3", "PHASE1", "PHASE3", "PHASE3", "PHASE4"],
        "overall_status": ["COMPLETED"] * 7 + ["RECRUITING"],
        "start_date": ["2005-06-01", "2010-04-01", "2018-09-01", "2014-01-01",
                       "2019-03-01", "2016-05-01", "2020-01-01", "2021-01-01"],
        "primary_completion_date": ["2007-08-01", "2014-01-01", "2020-12-01", "2017-06-01",
                                    "2020-08-01", "2019-04-01", "2022-12-01", None],
        "study_first_submitted_date": ["2006-01-01", "2009-12-01", "2018-06-01", "2013-09-01",
                                       "2018-12-01", "2016-03-01", "2019-11-01", "2020-12-01"],
        "results_first_submitted_date": [None, "2015-01-01", "2021-08-01", None,
                                         "2021-11-01", None, "2023-09-01", None],
        "enrollment": [400, 15460, 600, 320, 28, 120000, 800, 250],
        "is_fda_regulated_drug": [False, False, True, True, False, False, True, True],
    }))
    _w(tmp_path, "conditions", pd.DataFrame({
        "nct_id": [f"NCT0{i}" for i in range(1, 9)],
        "name": ["Falciparum Malaria", "Plasmodium Falciparum Malaria", "Uncomplicated Malaria",
                 "Plasmodium Vivax", "Malaria", "Malaria", "Type 2 Diabetes", "Hypertension"],
    }))
    _w(tmp_path, "browse_conditions", pd.DataFrame({
        "nct_id": [f"NCT0{i}" for i in range(1, 7)],
        "mesh_term": ["Malaria, Falciparum", "Malaria, Falciparum", "Malaria",
                      "Malaria, Vivax", "Malaria", "Malaria"],
    }))
    _w(tmp_path, "interventions", pd.DataFrame({
        "nct_id": ["NCT01", "NCT02", "NCT03", "NCT03", "NCT04", "NCT05", "NCT06", "NCT07", "NCT08"],
        "name": ["Artemether-lumefantrine 20/120mg pediatric", "RTS,S/AS01",
                 "Artesunate-mefloquine", "Dihydroartemisinin-piperaquine",
                 "Tafenoquine 300mg single dose", "PfSPZ Challenge",
                 "Dihydroartemisinin-piperaquine MDA", "Metformin", "Amlodipine"],
        "intervention_type": ["DRUG", "BIOLOGICAL", "DRUG", "DRUG", "DRUG", "BIOLOGICAL", "DRUG", "DRUG", "DRUG"],
    }))
    _w(tmp_path, "sponsors", pd.DataFrame({
        "nct_id": [f"NCT0{i}" for i in range(1, 9)],
        "name": ["London School of Hygiene and Tropical Medicine", "GlaxoSmithKline",
                 "Medicines for Malaria Venture", "GlaxoSmithKline", "Sanaria Inc.",
                 "World Health Organization", "Pfizer", "AstraZeneca"],
        "lead_or_collaborator": ["lead"] * 8,
        "agency_class": ["OTHER", "INDUSTRY", "OTHER", "INDUSTRY", "INDUSTRY",
                         "OTHER_GOV", "INDUSTRY", "INDUSTRY"],
    }))
    _w(tmp_path, "countries", pd.DataFrame({
        "nct_id": ["NCT01", "NCT01", "NCT02", "NCT02", "NCT03", "NCT04", "NCT05", "NCT06", "NCT07", "NCT08"],
        "name": ["Tanzania", "Kenya", "Mozambique", "Ghana", "Cambodia",
                 "Brazil", "United States", "Zambia", "United States", "United States"],
    }))
    _w(tmp_path, "facilities", pd.DataFrame({
        "nct_id": ["NCT01", "NCT01", "NCT02", "NCT02", "NCT03", "NCT04", "NCT05", "NCT06", "NCT07", "NCT08"],
        "country": ["Tanzania", "Kenya", "Mozambique", "Ghana", "Cambodia",
                    "Brazil", "United States", "Zambia", "United States", "United States"],
    }))
    _w(tmp_path, "eligibilities", pd.DataFrame({
        "nct_id": [f"NCT0{i}" for i in range(1, 9)],
        "minimum_age": ["6 Months", "5 Months", "18 Years", "16 Years", "18 Years",
                        "6 Months", "18 Years", "65 Years"],
        "maximum_age": ["59 Months", "17 Months", "65 Years", "65 Years", "55 Years",
                        "N/A", "75 Years", "N/A"],
        "criteria": [
            "Children 6-59 months with uncomplicated falciparum malaria",
            "Healthy infants 5-17 months",
            "Adults with uncomplicated P. falciparum",
            "Patients with confirmed P. vivax",
            "Healthy non-immune adults for sporozoite challenge",
            "All residents of treatment villages",
            "Type 2 diabetes",
            "Hypertension",
        ],
    }))
    _w(tmp_path, "design_outcomes", pd.DataFrame({
        "nct_id": ["NCT01", "NCT01", "NCT02", "NCT03", "NCT03", "NCT04", "NCT05", "NCT06"],
        "outcome_type": ["primary", "secondary", "primary", "primary", "secondary", "primary", "primary", "primary"],
        "measure": [
            "PCR-corrected adequate clinical and parasitological response (ACPR) at day 28",
            "Day 28 fever clearance",
            "Vaccine efficacy against clinical malaria",
            "Day 42 ACPR",
            "Time to recurrent parasitaemia (PCR-uncorrected)",
            "Recurrence of P. vivax parasitaemia at 6 months",
            "Time to first parasitemia after challenge",
            "Prevalence of asymptomatic P. falciparum infection at month 12",
        ],
        "time_frame": ["28 days", "28 days", "12 months", "42 days", "42 days", "180 days", "28 days", "12 months"],
    }))
    _w(tmp_path, "id_information", pd.DataFrame({
        "nct_id": ["NCT01", "NCT01", "NCT04"],
        "id_value": ["ISRCTN12345678", "PACTR201509001234567", "RBR-abc123"],
        "id_type": ["registry_id", "registry_id", "registry_id"],
    }))
    _w(tmp_path, "calculated_values", pd.DataFrame({
        "nct_id": [f"NCT0{i}" for i in range(1, 9)],
        "were_results_reported": [False, True, True, False, True, False, True, False],
        "months_to_report_results": [None, 7, 9, None, 5, None, 9, None],
    }))
    return tmp_path
