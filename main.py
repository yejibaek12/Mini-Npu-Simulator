from core import calculate_mac, compare_scores, measure_performance
from utils import load_data, normalize_label, input_3x3_matrix

def run_mode_1():
    print("\n# [모드 1] 사용자 입력 분석 시작")
    filter_a = input_3x3_matrix("필터 A")
    filter_b = input_3x3_matrix("필터 B")
    pattern = input_3x3_matrix("패턴")
    
    score_a = calculate_mac(pattern, filter_a)
    score_b = calculate_mac(pattern, filter_b)
    avg_time = measure_performance(pattern, filter_a)
    result = compare_scores(score_a, score_b)
    
    print("\n# [결과 리포트]")
    print(f"A 점수: {score_a} | B 점수: {score_b}")
    print(f"판정: {result} | 평균 연산 시간: {avg_time:.4f} ms")

def run_mode_2(data):
    if not data: return
    filters = data.get('filters', {})
    patterns = data.get('patterns', {})
    
    print("\n# [1] 필터 로드 및 분석 시작")
    pass_count = 0
    fail_list = []

    for p_id, p_content in patterns.items():
        try:
            # 1. ID에서 기대하는 N 사이즈 추출 (예: size_5_fail -> 5)
            n_val = int(p_id.split('_')[1])
            size_key = f"size_{n_val}"
            
            input_data = p_content.get('input', [])
            expected = normalize_label(p_content.get('expected', ''))

            # -------------------------------------------------------
            # [추가된 엄격한 크기 검증 로직]
            # 1) 행(Row)의 개수 검사
            if len(input_data) != n_val:
                raise ValueError(f"데이터 규격 불일치: 행 개수가 {n_val}개가 아님 (실제: {len(input_data)}개)")
            
            # 2) 각 열(Column)의 개수 검사
            for row_idx, row in enumerate(input_data):
                if len(row) != n_val:
                    raise ValueError(f"데이터 규격 불일치: {row_idx+1}번째 줄의 요소가 {n_val}개가 아님")
            # -------------------------------------------------------

            # 필터 존재 여부 확인
            if size_key not in filters:
                raise KeyError(f"해당 사이즈({size_key})에 맞는 필터 데이터가 없습니다.")

            filter_cross = filters[size_key]["Cross"]
            filter_x = filters[size_key]["X"]
            
            # 연산 및 판정
            score_cross = calculate_mac(input_data, filter_cross)
            score_x = calculate_mac(input_data, filter_x)
            pred_code = compare_scores(score_cross, score_x)
            
            actual = "Cross" if pred_code == "A" else "X" if pred_code == "B" else "UNDECIDED"
            
            if actual == expected:
                pass_count += 1
                print(f"{p_id} | 결과: {actual} | PASS")
            else:
                status = f"FAIL (판정 불일치 - 예상:{expected}, 실제:{actual})"
                fail_list.append(f"{p_id}: {status}")
                print(f"{p_id} | {status}")

        except (ValueError, KeyError) as e:
            # 크기가 안 맞거나 필터가 없는 경우 이곳으로 점프합니다.
            error_msg = f"FAIL (오류: {e})"
            print(f"{p_id} | {error_msg}")
            fail_list.append(f"{p_id}: {error_msg}")

    # 결과 요약 출력

    print(f"\n# [3] 결과 요약: {pass_count}/{len(patterns)} 통과")
    if fail_list:
        for f in fail_list: print(f"- {f}")

def analyze_performance_by_size():
    """크기별 성능 리포트"""
    sizes = [3, 5, 13, 25]
    print("\n" + "="*45)
    print(f"{'Size (NxN)':<15} | {'Avg Time (ms)':<15}")
    print("-" * 45)
    for n in sizes:
        pattern = [[0.5]*n for _ in range(n)]
        avg_time = measure_performance(pattern, pattern)
        print(f"{f'{n}x{n}':<15} | {avg_time:<15.4f}")
    print("="*45)

if __name__ == "__main__":
    while True:
        print("\n" + "="*30)
        print("   === Mini NPU Simulator ===")
        print("1: 모드 1 (사용자 입력 3x3)")
        print("2: 모드 2 (JSON 일괄 분석)")
        print("3: 성능 분석 리포트")
        print("q: 프로그램 종료")
        print("="*30)
        
        choice = input("선택하세요: ").lower().strip()
        
        if choice == '1':
            run_mode_1()
        elif choice == '2':
            data = load_data('data.json')
            if data: 
                run_mode_2(data)
                analyze_performance_by_size()
        elif choice == '3':
            analyze_performance_by_size()
        elif choice in ['q', '0', 'exit', 'quit']:
            print("프로그램을 종료합니다. 안녕히 가세요!")
            break  # while 루프를 탈출하여 프로그램을 종료합니다.
        else:
            print("잘못된 선택입니다. 다시 입력해주세요.")