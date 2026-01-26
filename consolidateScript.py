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
            unique_id = row[0]  # Col A
            item = row[1]  # Col B
            remarks = row[9]  # Col J
            uom = row[15]  # Col P
            qty = float(row[12]) if pd.notna(row[12]) else 0  # Col M
            price_row = float(row[20]) if pd.notna(row[20]) else 0  # Col U
        except IndexError:
            continue

        if not unique_id or not item:
            continue

        key = f"{unique_id}|{item}|{remarks}|{uom}"

        if key not in inventory_map:
            inventory_map[key] = {
                "uniqueId": unique_id,
                "item": item,
                "remarks": remarks,
                "uom": uom,
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
            entry["remarks"],
            entry["uom"],
            entry["q_total"],
            entry["p_total"],
            unit_price
        ])

    result_df = pd.DataFrame(output, columns=[
        "unique_id", "item", "remarks", "uom", "q_total", "p_total", "unit_price"
    ])

    # Write to "Processed" sheet (overwrite)
    with pd.ExcelWriter(file_path, mode="a", if_sheet_exists="replace") as writer:
        result_df.to_excel(writer, sheet_name="Processed", index=False)

    print("Done")


if __name__ == "__main__":
    consolidate_inventory("inventory.xlsx")  # replace with your Excel file path