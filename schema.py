# schema.py
# Defines the expected data type for every column in the report.
# Valid types: "date", "string", "numeric", "boolean"
# Edit this file if columns are added, removed, or retyped in the source report.

COLUMN_SCHEMA = {
    # --- Dates ---
    "Effective Date":                           "date",
    "End Date":                                 "date",

    # --- Categorical / Text ---
    "Carrier Type":                             "string",
    "Carrier_Forwarder Name":                   "string",
    "Origin Continent":                         "string",
    "Origin Country":                           "string",
    "Origin Port":                              "string",
    "Vendor Name":                              "string",
    "Intco Terms":                              "string",
    "Destination Port of Discharge Coast":      "string",
    "Destination Port Of Discharge":            "string",
    "Move IPI_RIPI_CY":                         "string",
    "Destination CY Location":                  "string",
    "Drop / Live Unload":                       "string",
    "Branch Destination":                       "string",
    "Customer Name":                            "string",
    "Move":                                     "string",

    # --- All-In Totals ---
    "20' ALL IN":                               "numeric",
    "40' ALL IN":                               "numeric",
    "40HC ALL IN":                              "numeric",

    # --- Ocean Totals ---
    "Total Ocean 20'":                          "numeric",
    "Total Ocean 40'":                          "numeric",
    "Total Ocean 40HC":                         "numeric",

    # --- EFC ---
    "20' EFC":                                  "numeric",
    "40' EFC":                                  "numeric",
    "40HC EFC":                                 "numeric",

    # --- Dray / Chassis ---
    "Total Dray 2":                             "numeric",
    "Total Chassis":                            "numeric",

    # --- CUC / FCA / Domestic Copies (reference columns) ---
    "20' CUC - Copy":                           "numeric",
    "40HC CUC - Copy":                          "numeric",
    "20' FCA Origin Charges - Copy":            "numeric",
    "40HC FCA Origin Charges - Copy":           "numeric",
    "20' Domestic Charges - Copy":              "numeric",
    "40HC Domestic Charges - Copy":             "numeric",

    # --- Miscellaneous ---
    "Per Diem Free Days":                       "numeric",

    # --- 20' Charge Breakdown ---
    "20' Ocean Freight Base Charge":            "numeric",
    "20' PSS":                                  "numeric",
    "20' Emergency Fuel Surcharge":             "numeric",
    "20' Origin Arb":                           "numeric",
    "20' Bunker":                               "numeric",
    "20' Low Sulfur":                           "numeric",
    "20' CUC":                                  "numeric",
    "20' FCA Origin Charges":                   "numeric",
    "20' Domestic Charges":                     "numeric",
    "20' Add on Charges":                       "numeric",
    "20' Contract Carrier Additional Charges":  "numeric",

    # --- 40' Charge Breakdown ---
    "40' Ocean Freight Base Charge":            "numeric",
    "40' PSS":                                  "numeric",
    "40' Emergency Fuel Surcharge":             "numeric",
    "40' Origin Arb":                           "numeric",
    "40' Bunker":                               "numeric",
    "40' Low Sulfur":                           "numeric",
    "40' CUC":                                  "numeric",
    "40' FCA Origin Charges":                   "numeric",
    "40' Domestic Charges":                     "numeric",
    "40' Add on Charges":                       "numeric",
    "40' Contract Carrier Additional Charges":  "numeric",

    # --- 40HC Charge Breakdown ---
    "40HC Ocean Freight Base Charge":           "numeric",
    "40HC PSS":                                 "numeric",
    "40HC Emergency Fuel Surcharge":            "numeric",
    "40HC Origin Arb":                          "numeric",
    "40HC Bunker":                              "numeric",
    "40HC Low Sulfur":                          "numeric",
    "40HC CUC":                                 "numeric",
    "40HC FCA Origin Charges":                  "numeric",
    "40HC Domestic Charges":                    "numeric",
    "40HC Add on Charges":                      "numeric",
    "40HC Contract Carrier Additional Charges": "numeric",
}