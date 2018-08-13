def calculate_interval(values):
    interval = None
    last_value = None
    for value in sorted(values):
        if last_value is not None:
            next_interval = value - last_value
            if next_interval == interval:
                return interval
            interval = next_interval
        last_value = value
    return interval

def get_next_available_bit(bits):
    bit = 1
    for _ in range(63):
        if not bit in bits:
            return bit
        bit <<= 1
    return 0
