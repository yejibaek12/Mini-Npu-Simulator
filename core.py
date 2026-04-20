import time

def calculate_mac(pattern, filter_data):
    """패턴과 필터를 받아서 MAC(Multiply-Accumulate) 연산을 수행"""
    total_score = 0.0
    n = len(pattern)
    for i in range(n):
        for j in range(n):
            total_score += pattern[i][j] * filter_data[i][j]
    return total_score

def compare_scores(score_a, score_b):
    """두 점수를 비교하여 판정 결과를 반환"""
    epsilon = 1e-9
    if abs(score_a - score_b) < epsilon:
        return "판정불가"
    return "A" if score_a > score_b else "B"

def measure_performance(pattern, filter_data):
    """10회 반복 측정하여 평균 연산 시간(ms) 계산"""
    start_time = time.perf_counter()
    for _ in range(10):
        calculate_mac(pattern, filter_data)
    end_time = time.perf_counter()
    return ((end_time - start_time) / 10) * 1000