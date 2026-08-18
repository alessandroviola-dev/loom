def summarize_scores(rows):
    total = 0.0
    count = 0
    invalid = 0

    for row in rows:
        if "score" not in row:
            invalid += 1
            continue

        value = row["score"]
        if isinstance(value, bool):
            invalid += 1
            continue

        if isinstance(value, (int, float)):
            score = float(value)
        elif isinstance(value, str):
            try:
                score = float(value.strip())
            except (TypeError, ValueError):
                invalid += 1
                continue
        else:
            invalid += 1
            continue

        if score < 0 or score > 100:
            invalid += 1
            continue

        total += score
        count += 1

    return {
        "count": count,
        "invalid": invalid,
        "average": None if count == 0 else round(total / count, 2),
    }
