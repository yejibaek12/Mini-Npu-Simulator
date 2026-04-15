# **Mini NPU Simulator 개발 개요**
본 프로젝트는 컴퓨터가 시각적 형태를 인식하는 원리인 **MAC(Multiply-Accumulate) 연산**을 이해하고, 이를 통해 입력된 패턴이 특정 필터(십자가 또는 X)와 얼마나 유사한지 판별하는 시뮬레이터를 개발하는 것입니다.

단순 연산을 넘어, 실제 AI 모델이 겪는 **부동소수점 오차 처리**, **데이터 정규화**, 그리고 크기 증가에 따른 **시간 복잡도 <code>O(N<sup>2</sup>)</code> 분석**까지 포함하는 종합적인 소프트웨어 테스트 및 성능 분석입니다. 

# ☑️ **단계별 체크리스트**
**1단계: 핵심 연산 로직 및 데이터 구조 설계**
- [ ] 데이터 저장 구조 정의: n×n 크기의 2차원 배열을 저장하고 특정 위치 $(x, y)$의 값을 읽고 쓸 수 있는 구조 설계.
- [ ] MAC 연산 함수 구현: 외부 라이브러리(NumPy 등) 없이 반복문만 사용하여 '위치별 곱셈 후 누적 합산' 로직 구현.
- [ ] 라벨 정규화 로직: +, cross는 Cross로, x는 X로 표준화하는 함수 작성.
- [ ] 부동소수점 비교 정책: 두 점수의 차이가 1e-9 미만일 때 동점(UNDECIDED)으로 처리하는 오차 허용 로직 적용.

**2단계: 모드 1 - 사용자 입력 처리 (3x3)**
- [ ] 입력 인터페이스: 필터 A, B와 패턴 데이터를 콘솔로 입력받는 흐름 구현.
- [ ] 입력 검증(Validation): 행/열 개수 불일치나 숫자 파싱 오류 시 안내 메시지 출력 및 재입력 유도.
- [ ] 결과 출력: A/B 점수, 판정 결과, 그리고 10회 반복 측정을 통한 평균 연산 시간(ms) 출력.

**3단계: 모드 2 - JSON 데이터 분석 (Batch)**
- [ ] JSON 데이터 로드: data.json 파일을 읽어 filters와 patterns 파싱.
- [ ] 스키마 및 크기 검증: 필터와 패턴의 크기가 맞지 않을 경우 프로그램을 종료하지 않고 해당 케이스만 FAIL 처리.
- [ ] 일괄 판정: 각 패턴에 대해 적절한 필터를 선택하여 연산 후 expected 값과 비교하여 PASS/FAIL 판정.

**4단계: 성능 분석 및 리포트 작성**
- [ ] 성능 측정: 3×3, 5×5, 13×13, 25×25 각 크기별로 10회씩 측정하여 평균 시간 계산.
- [ ] 성능 표 출력: 크기(N×N), 평균 시간(ms), 연산 횟수($N^2$)를 포함한 표 작성.
- [ ] 결과 요약: 전체 테스트 수, 통과 수, 실패 수 및 실패 케이스 목록 콘솔 출력.

**5단계: 최종 제출물 정리**
- [ ] README.md 작성: 실행 방법, 구현 요약(정규화, 오차 정책), 실패 원인 분석 및 시간 복잡도 <code>O(N<sup>2</sup>)</code> 분석 리포트(10줄 이상) 포함.
- [ ] 코드 정리: Python 3.8 이상 환경 준수 및 외부 라이브러리 사용 여부 최종 확인.

<br>

# **1. 핵심 연산 로직 구현하기 (main.py)**
## (1) MAC 연산 함수 만들기
```bash
$ touch main.py
```
```python
def calculate_mac(pattern, filter_data):
    # 패턴과 필터를 받아서 MAC(Multiply-Accumulate) 연산을 수행
    # pattern: n x n 크기의 2차원 리스트
    # filter_data: n x n 크기의 2차원 리스트
    
    total_score = 0.0
    n = len(pattern) # 배열의 크기 (예: 3, 5, 13...)

    # 행(row)을 돌고, 그 안에서 열(column)을 돎
    for i in range(n):
        for j in range(n):
            # 같은 위치의 숫자끼리 곱해서 누적해서 더함
            total_score += pattern[i][j] * filter_data[i][j]
            
    return total_score
```

## (2) 부동소수점 오차 처리 정책 적용
```python
def compare_scores(score_a, score_b):
    # 두 점수를 비교하여 판정 결과를 반환
    
    # 허용 오차(epsilon): 1e-9
    epsilon = 1e-9 # 0.000000001
    
    # 두 값의 차이의 절대값이 epsilon보다 작으면 '동점'으로 처리
    if abs(score_a - score_b) < epsilon:
        return "UNDECIDED"
    elif score_a > score_b:
        return "A"
    else:
        return "B"
```

## (3) 라벨 정규화(표준화) 점수
```python
def normalize_label(label):
    # 입력된 라벨을 'Cross' 또는 'X'로 통일
    label = str(label).lower().strip() # 소문자로 바꾸고 공백 제거
    
    if label in ['+', 'cross']:
        return "Cross"
    elif label in ['x']:
        return "X"
    return label # 해당하지 않는 경우 그대로 반환
```

<br>

# **2. 모드 1 구현하기 (사용자 입력 및 검증)**
- 사용자가 실수로 숫자를 적게 입력하거나 문자를 입력했을 때 프로그램이 꺼지지 않게함
- 입력 형식 오류 시 안내 문구 출력 및 재입력 유도
## (1) 3x3 배열을 입력받는 함수
```python
def input_3x3_matrix(name):
    print(f"{name} (3줄 입력, 공백 구분)")
    matrix = []
    while len(matrix) < 3:
        try:
            line = input().split()
            # 숫자가 3개가 아니면 에러 발생
            if len(line) != 3:
                raise ValueError("입력 형식 오류: 각 줄에 3개의 숫자를 공백으로 구분해 입력하세요.")
            
            # 문자열을 숫자로 변환해서 한 줄(row) 만들기
            row = [float(x) for x in line]
            matrix.append(row)
        except ValueError as e:
            print(e)
            print("다시 입력해 주세요.")
    return matrix
```

## (2) 시간 측정 기능 (성능 분석 맛보기)
```python
import time

def measure_performance(pattern, filter_data):
    # 10회 반복 측정하여 평균 시간 계산
    start_time = time.perf_counter()
    for _ in range(10):
        calculate_mac(pattern, filter_data)
    end_time = time.perf_counter()
    
    # 초 단위 차이를 ms(밀리초)로 변환
    avg_time_ms = ((end_time - start_time) / 10) * 1000
    return avg_time_ms
```

## (3) 모드 1 실행 로직 완성
```python
def run_mode_1():
    print("\n# [1] 필터 입력")
    filter_a = input_3x3_matrix("필터 A")
    filter_b = input_3x3_matrix("필터 B")
    
    print("\n# [2] 패턴 입력")
    pattern = input_3x3_matrix("패턴")
    
    # 1. MAC 연산 수행
    score_a = calculate_mac(pattern, filter_a)
    score_b = calculate_mac(pattern, filter_b)
    
    # 2. 성능 측정
    avg_time = measure_performance(pattern, filter_a) # 하나만 측정해도 무방
    
    # 3. 결과 판정
    result = compare_scores(score_a, score_b)
    
    print("\n# [3] MAC 결과")
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"연산 시간(평균/10회): {avg_time:.3f} ms")
    
    if result == "UNDECIDED":
        print(f"판정: 판정 불가 (|A-B| < 1e-9)") [cite: 260]
    else:
        print(f"판정: {result}")
```
<br>

 # **3. 모드 2: JSON 데이터 분석**
 ## (1) JSON 파일 읽기 (데이터 불러오기)
```python
import json

def load_data(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data
```

## (2) 데이터 검증 및 일괄 판정 (핵심 로직)
```python
def run_mode_2(data):
    filters = data['filters']    # 필터 정보들 (Cross, X 등)
    patterns = data['patterns']  # 판정해야 할 패턴들
    
    results = [] # 결과를 저장할 빈 리스트

    for p in patterns:
        # 1. 라벨 정규화 (예: 'cross' -> 'Cross')
        expected = normalize_label(p['label'])
        
        # 2. 필터 데이터 가져오기 (이름에 맞는 필터 선택)
        # 예시: 'Cross' 필터와 'X' 필터의 데이터를 각각 가져옴
        score_cross = calculate_mac(p['data'], filters['Cross'])
        score_x = calculate_mac(p['data'], filters['X'])
        
        # 3. 점수 비교 및 판정
        prediction_code = compare_scores(score_cross, score_x)
        
        # 4. 판정 코드를 실제 이름으로 변환
        if prediction_code == "A":
            actual = "Cross"
        elif prediction_code == "B":
            actual = "X"
        else:
            actual = "UNDECIDED"

        # 5. 정답(expected)과 결과(actual) 비교
        is_pass = (actual == expected)
        results.append(is_pass)
        
        print(f"패턴 ID: {p['id']} | 결과: {'PASS' if is_pass else 'FAIL'} (예상: {expected}, 실제: {actual})")
```

<br>

# **4. 성능 분석 및 리포트 작성**
## (1) 크기별 성능 측정 로직
```python 
 def analyze_performance_by_size():
    # 측정할 크기들 (N x N)
    sizes = [3, 5, 13, 25]
    performance_results = []

    for n in sizes:
        # 1. 테스트용 더미(Dummy) 데이터 생성
        # 모든 칸이 0.5인 n x n 배열을 만듦
        pattern = [[0.5 for _ in range(n)] for _ in range(n)]
        filter_data = [[0.5 for _ in range(n)] for _ in range(n)]
        
        # 2. 앞서 만든 함수로 평균 시간 측정
        avg_time = measure_performance(pattern, filter_data)
        
        # 3. 결과 저장 (크기, 평균 시간, 실제 연산 횟수 N^2)
        performance_results.append({
            'size': f"{n}x{n}",
            'time': avg_time,
            'ops': n * n
        })
    
    return performance_results
```

## (2) 시간 복잡도 $O(N^2)$ 리포트 이해하기
- N=3일 때: 연산 횟수는 3×3=9번
- N=25일 때: 연산 횟수는 25×25=625번
- 분석 포인트: 가로/세로 크기는 약 8배 커졌지만, 실제 연산량은 약 70배(625÷9) 늘어난다. 

## (3) 결과 요약 및 출력
```python
def print_report(results):
    print("\n" + "="*45)
    print(f"{'Size (NxN)':<15} | {'Avg Time (ms)':<15} | {'Ops (N^2)':<10}")
    print("-" * 45)
    
    for res in results:
        print(f"{res['size']:<15} | {res['time']:<15.4f} | {res['ops']:<10}")
    print("="*45)
```

