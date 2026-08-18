def window_sum(values, size):
    if not isinstance(size, int) or size <= 0:
        raise ValueError("size must be a positive integer")
    if size > len(values):
        return []

    output = []
    running = sum(values[:size])
    for index in range(size, len(values)):
        output.append(running)
        running += values[index] - values[index - size]
    return output
