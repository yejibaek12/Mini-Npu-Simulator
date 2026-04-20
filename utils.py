import json

def load_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"오류: {file_path} 파일을 찾을 수 없습니다.")
        return None

def normalize_label(label):
    """입력된 라벨을 'Cross' 또는 'X'로 통일"""
    label = str(label).lower().strip()
    if label in ['+', 'cross']:
        return "Cross"
    elif label in ['x']:
        return "X"
    return label

def input_3x3_matrix(name):
    """3x3 배열을 콘솔로 입력받음"""
    print(f"{name} (3줄 입력, 공백 구분)")
    matrix = []
    while len(matrix) < 3:
        try:
            line = input().split()
            if len(line) != 3:
                raise ValueError("입력 형식 오류: 각 줄에 3개의 숫자를 공백으로 구분하세요.")
            matrix.append([float(x) for x in line])
        except ValueError as e:
            print(e)
    return matrix