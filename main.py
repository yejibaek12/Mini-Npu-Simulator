# MAC 연산 함수 만들기
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
 


# 부동소수점 오차 처리 함수
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
    


## (3) 라벨 정규화(표준화) 점수
def normalize_label(label):
    # 입력된 라벨을 'Cross' 또는 'X'로 통일
    label = str(label).lower().strip() # 소문자로 바꾸고 공백 제거
    
    if label in ['+', 'cross']:
        return "Cross"
    elif label in ['x']:
        return "X"
    return label # 해당하지 않는 경우 그대로 반환