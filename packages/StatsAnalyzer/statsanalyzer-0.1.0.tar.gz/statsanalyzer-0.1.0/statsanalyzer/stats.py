from typing import List, Tuple
import math

def mean(data: List[float]) -> float:
    return sum(data) / len(data) if data else 0.0

def median(data: List[float]) -> float:
    n = len(data)
    if n == 0:
        return 0.0
    sorted_data = sorted(data)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_data[mid-1] + sorted_data[mid]) / 2
    else:
        return sorted_data[mid]

def variance(data: List[float]) -> float:
    if not data:
        return 0.0
    m = mean(data)
    return sum((x - m)**2 for x in data) / len(data)

def std_dev(data: List[float]) -> float:
    return math.sqrt(variance(data))

def min_max(data: List[float]) -> Tuple[float, float]:
    if not data:
        return (0.0, 0.0)
    return (min(data), max(data))

def summary(data: List[float]) -> dict:
    return {
        "mean": mean(data),
        "median": median(data),
        "variance": variance(data),
        "std_dev": std_dev(data),
        "min": min_max(data)[0],
        "max": min_max(data)[1],
        "count": len(data)
    }
