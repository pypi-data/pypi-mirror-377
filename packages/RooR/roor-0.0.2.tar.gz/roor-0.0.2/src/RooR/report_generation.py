# -*- coding: utf-8 -*-
"""
Module for generating analysis reports.
"""

import json
import pandas as pd

def generate_json_report(data, output_file):
    """
    Generates a JSON report from a dictionary.
    
    Args:
        data (dict): The data to include in the report.
        output_file (str): The path to the output JSON file.
    """
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"JSON report generated at {output_file}")

def generate_csv_report(data, output_file):
    """
    Generates a CSV report from a pandas DataFrame.
    
    Args:
        data (pandas.DataFrame): The data to include in the report.
        output_file (str): The path to the output CSV file.
    """
    data.to_csv(output_file, index=False)
    print(f"CSV report generated at {output_file}")
