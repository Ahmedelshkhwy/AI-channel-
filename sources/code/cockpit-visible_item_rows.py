def visible_item_rows() -> list[dict[str, Any]]:
    allowed = allowed_branches()
    with get_db() as db:
        rows = [dict(row) for row in db.execute("SELECT * FROM items")]
    return rows if allowed is None else [row for row in rows if row["branch"] in allowed]
