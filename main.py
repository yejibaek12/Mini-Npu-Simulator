import time
import json

def load_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)  # json 라이브러리를 사용해 데이터를 가져옵니다.
    except FileNotFoundError:
        print(f"오류: {file_path} 파일을 찾을 수 없습니다.")
        return None

# ==========================================
# 1단계: 핵심 연산 로직 (MAC 및 유틸리티)
# ==========================================

def calculate_mac(pattern, filter_data):
    """패턴과 필터를 받아서 MAC(Multiply-Accumulate) 연산을 수행"""
    total_score = 0.0
    n = len(pattern)
    for i in range(n):
        for j in range(n):
            total_score += pattern[i][j] * filter_data[i][j]
    return total_score

def compare_scores(score_a, score_b):
    """두 점수를 비교하여 판정 결과를 반환 (부동소수점 오차 처리)"""
    epsilon = 1e-9
    if abs(score_a - score_b) < epsilon:
        return "UNDECIDED"
    elif score_a > score_b:
        return "A"
    else:
        return "B"

def normalize_label(label):
    """입력된 라벨을 'Cross' 또는 'X'로 통일"""
    label = str(label).lower().strip()
    if label in ['+', 'cross']:
        return "Cross"
    elif label in ['x']:
        return "X"
    return label

# ==========================================
# 2단계: 모드 1 - 사용자 입력 처리
# ==========================================

def input_3x3_matrix(name):
    """3x3 배열을 콘솔로 입력받음"""
    print(f"{name} (3줄 입력, 공백 구분)")
    matrix = []
    while len(matrix) < 3:
        try:
            line = input().split()
            if len(line) != 3:
                raise ValueError("입력 형식 오류: 각 줄에 3개의 숫자를 공백으로 구분해 입력하세요.")
            row = [float(x) for x in line]
            matrix.append(row)
        except ValueError as e:
            print(e)
            print("다시 입력해 주세요.")
    return matrix

def measure_performance(pattern, filter_data):
    """10회 반복 측정하여 평균 연산 시간(ms) 계산"""
    start_time = time.perf_counter()
    for _ in range(10):
        calculate_mac(pattern, filter_data)
    end_time = time.perf_counter()
    avg_time_ms = ((end_time - start_time) / 10) * 1000
    return avg_time_ms

def run_mode_1():
    """모드 1 실행 로직"""
    print("\n# [모드 1] 사용자 입력 분석 시작")
    filter_a = input_3x3_matrix("필터 A")
    filter_b = input_3x3_matrix("필터 B")
    pattern = input_3x3_matrix("패턴")
    
    score_a = calculate_mac(pattern, filter_a)
    score_b = calculate_mac(pattern, filter_b)
    avg_time = measure_performance(pattern, filter_a)
    result = compare_scores(score_a, score_b)
    
    print("\n# [결과 리포트]")
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"판정: {result}")
    print(f"연산 시간(평균): {avg_time:.4f} ms")

# ==========================================
# 3단계: 모드 2 - JSON 일괄 분석
# ==========================================

def run_mode_2(data):
    if not data: return
    filters = data.get('filters', {})
    patterns = data.get('patterns', [])
    
    print("\n# [1] 필터 로드")
    print("#----")
    loaded_sizes = sorted(list(set(int(k.split('_')[1]) for k in filters.keys())))
    for size in loaded_sizes:
        print(f"✓ size_{size} 필터 로드 완료 (Cross, X)")
    
    print("\n# [2] 패턴 분석 (라벨 정규화 적용)")
    print("#--------")
    
    pass_count = 0
    fail_list = [] # 실패 케이스 저장용

    for p in patterns:
        try:
            # 1. 키(ID)에서 N 추출
            n = int(p['id'].split('_')[1])
            
            # 2. 필터 선택
            filter_cross_key = f"size_{n}_Cross"
            filter_x_key = f"size_{n}_X"
            
            # 3. 데이터 및 라벨 가져오기
            input_data = p['input']
            label_data = p['expected']
            
            # 4. 크기 검증 
            if len(input_data) != n:
                raise ValueError(f"크기 불일치 (필요: {n}x{n})")

            # 5. 연산 및 판정
            expected = normalize_label(label_data) # 라벨 정규화
            score_cross = calculate_mac(input_data, filters[filter_cross_key])
            score_x = calculate_mac(input_data, filters[filter_x_key])
            
            pred_code = compare_scores(score_cross, score_x) # epsilon 기반 비교
            actual = "Cross" if pred_code == "A" else "X" if pred_code == "B" else "UNDECIDED"
            
            is_pass = (actual == expected)
            
            if is_pass: 
                pass_count += 1
                status = "PASS"
            else:
                status = "FAIL"
                fail_list.append(f"{p['id']}: 판정 불일치 (예상:{expected}, 실제:{actual})")
            
            print(f"{p['id']}")
            print(f"Cross 점수: {score_cross}")
            print(f"X 점수: {score_x}")
            print(f"판정: {actual} | expected: {expected} | {status}")
            print("-" * 20)

        except (ValueError, KeyError) as e:
            error_msg = f"{p['id']}: FAIL (사유: {e})"
            print(error_msg)
            fail_list.append(error_msg)
            continue

    # [3] 결과 요약 출력
    print(f"\n# [3] 결과 요약")
    print("#--")
    print(f"총 테스트: {len(patterns)}개")
    print(f"통과: {pass_count}개")
    print(f"실패: {len(patterns) - pass_count}개")
    
    if fail_list:
        print("\n실패 케이스:")
        for fail in fail_list:
            print(f"- {fail}")

# ==========================================
# 4단계: 성능 분석 리포트
# ==========================================

def analyze_performance_by_size():
    """크기별 성능 측정 및 리포트 출력"""
    sizes = [3, 5, 13, 25]
    results = []

    for n in sizes:
        # 더미 데이터 생성 (리스트 컴프리헨션)
        pattern = [[0.5 for _ in range(n)] for _ in range(n)]
        filter_data = [[0.5 for _ in range(n)] for _ in range(n)]
        
        avg_time = measure_performance(pattern, filter_data)
        results.append({'size': f"{n}x{n}", 'time': avg_time, 'ops': n * n})
    
    # 리포트 출력
    print("\n" + "="*45)
    print(f"{'Size (NxN)':<15} | {'Avg Time (ms)':<15} | {'Ops (N^2)':<10}")
    print("-" * 45)
    for res in results:
        print(f"{res['size']:<15} | {res['time']:<15.4f} | {res['ops']:<10}")
    print("="*45)

# ==========================================
# 메인 실행부
# ==========================================

if __name__ == "__main__":
    print("=== Mini NPU Simulator ===")
    print("1: 모드 1 (사용자 입력 3x3)")
    print("2: 모드 2 (JSON 일괄 분석)")
    print("3: 성능 분석 리포트")
    
    choice = input("선택하세요: ")
    
    if choice == '1':
        run_mode_1()
    elif choice == '2':
        data = load_data('data.json')
        if data: 
            run_mode_2(data)
            analyze_performance_by_size() # 분석 후 성능 리포트 자동 출력
    elif choice == '3':
        analyze_performance_by_size()
    else:
        print("잘못된 선택입니다.")