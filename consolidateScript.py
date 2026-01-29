import pandas as pd

def split_num_unit(s):
    """Split a string like '10grams' into (10.0, 'grams')."""
    if pd.isna(s):
        return 0.0, ""
    s = str(s).strip()
    num_part = ""
    unit_part = ""
    for ch in s:
        if ch.isdigit() or ch == ".":   # keep digits and decimals
            num_part += ch
        else:
            unit_part += ch
    try:
        num_val = float(num_part) if num_part else 0.0
    except ValueError:
        num_val = 0.0
    return num_val, unit_part

def consolidate_inventory(file_path):
    # Load Excel file
    xls = pd.ExcelFile(file_path)
    source_df = pd.read_excel(xls, "Raw", header=None)

    # Start from row 9 (index 8 in pandas)
    data = source_df.iloc[8:].reset_index(drop=True)

    inventory_map = {}

    # Aggregate data
    for _, row in data.iterrows():
        try:
            unique_id = row[0]   # Col A
            item = row[1]        # Col B
            brand = row[3]       # Col D (new identifier)
            remarks = row[4]     # Col E
            uom = row[9]         # Col J
            qty = float(row[7]) if pd.notna(row[7]) else 0   # Col H
            price_row = float(row[14]) if pd.notna(row[14]) else 0  # Col O
            units_raw = row[13]  # Col N (only for split, not grouping)
        except IndexError:
            continue

        if not unique_id or not item:
            continue

        # Normalize remarks/uom/brand to string
        brand = str(brand) if pd.notna(brand) else ""
        remarks = str(remarks) if pd.notna(remarks) else ""
        uom = str(uom) if pd.notna(uom) else ""

        # Split units into numeric + text (not part of key)
        unit_value, unit_name = split_num_unit(units_raw)

        # Consolidation key (exclude units_raw)
        key = f"{unique_id}|{item}|{brand}|{remarks}|{uom}"

        if key not in inventory_map:
            inventory_map[key] = {
                "uniqueId": unique_id,
                "item": item,
                "brand": brand,
                "remarks": remarks,
                "uom": uom,
                "unit_value": unit_value,
                "unit_name": unit_name,
                "q_total": 0,
                "p_total": 0
            }

        inventory_map[key]["q_total"] += qty
        inventory_map[key]["p_total"] += price_row

    # Prepare output DataFrame
    output = []
    for entry in inventory_map.values():
        unit_price = 0 if entry["q_total"] == 0 else entry["p_total"] / entry["q_total"]
        output.append([
            entry["uniqueId"],
            entry["item"],
            entry["brand"],
            entry["remarks"],
            entry["uom"],
            entry["unit_value"],
            entry["unit_name"],
            entry["q_total"],
            entry["p_total"],
            unit_price
        ])

    result_df = pd.DataFrame(output, columns=[
        "unique_id", "item", "brand", "remarks", "uom",
        "unit_value", "unit_name", "q_total", "p_total", "unit_price"
    ])

    # 🔑 Final fix: force all object columns to string
    for col in result_df.select_dtypes(include="object").columns:
        result_df[col] = result_df[col].astype(str)

    return result_df