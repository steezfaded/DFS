#!/usr/bin/env python3
"""Lineup ingestion placeholder using public lineup files.

This script supports manual CSV lineup import. Expected columns:
name,team,batting_order,opponent
"""
from __future__ import annotations
import argparse
import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    args = parser.parse_args()
    df = pd.read_csv(args.file)
    print(f"Loaded {len(df)} lineup rows for downstream custom integration.")


if __name__ == "__main__":
    main()
