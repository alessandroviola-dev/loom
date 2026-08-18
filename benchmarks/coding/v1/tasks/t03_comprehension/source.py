def assign_jobs(capacities, jobs):
    remaining = list(capacities)
    assignments = []

    for job in jobs:
        chosen = -1
        for index, available in enumerate(remaining):
            if available >= job:
                chosen = index
                remaining[index] -= job
                break
        assignments.append(chosen)

    return assignments
