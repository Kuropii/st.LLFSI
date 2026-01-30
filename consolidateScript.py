import pandas as pd

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
            brand = row[3]       # Col D
            remarks = row[4]     # Col E
            uom = row[9]         # Col J
            qty = float(row[7]) if pd.notna(row[7]) else 0   # Col H
            weight_volume = float(row[8]) if pd.notna(row[8]) else 0  # Col I (new identifier)
            price_row = float(row[14]) if pd.notna(row[14]) else 0    # Col O
        except IndexError:
            continue

        if not unique_id or not item:
            continue

        # Normalize strings
        brand = str(brand) if pd.notna(brand) else ""
        remarks = str(remarks) if pd.notna(remarks) else ""
        uom = str(uom) if pd.notna(uom) else ""

        # Consolidation key (exclude weight/volume from key, treat as numeric sum)
        key = f"{unique_id}|{item}|{brand}|{remarks}|{uom}"

        if key not in inventory_map:
            inventory_map[key] = {
                "uniqueId": unique_id,
                "item": item,
                "brand": brand,
                "remarks": remarks,
                "uom": uom,
                "q_total": 0,
                "p_total": 0,
                "wv_total": 0   # new aggregated field
            }

        inventory_map[key]["q_total"] += qty
        inventory_map[key]["p_total"] += price_row
        inventory_map[key]["wv_total"] += weight_volume

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
            entry["wv_total"],   # aggregated weight/volume
            entry["q_total"],
            entry["p_total"],
            unit_price
        ])

    result_df = pd.DataFrame(output, columns=[
        "unique_id", "item", "brand", "remarks", "uom",
        "weight_volume_total", "q_total", "p_total", "unit_price"
    ])

    # 🔑 Final fix: force all object columns to string
    for col in result_df.select_dtypes(include="object").columns:
        result_df[col] = result_df[col].astype(str)

    return result_df