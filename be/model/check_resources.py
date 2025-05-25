import os
import torch
import joblib

def check_file(path, description):
    if os.path.exists(path):
        print(f"✅ {description} 존재함: {path}")
    else:
        print(f"❌ {description} 없음: {path}")

def check_model_weights(path):
    try:
        state_dict = torch.load(path, map_location='cpu')
        print(f"\n📦 모델 파라미터 목록 ({path}):")
        for k, v in state_dict.items():
            print(f" - {k}: {tuple(v.shape)}")
    except Exception as e:
        print(f"❌ 모델 로드 실패: {e}")

def check_label_encoders(paths):
    for path, name in paths:
        try:
            obj = joblib.load(path)
            print(f"✅ {name} 로딩 성공: {path}, 클래스 수 = {len(obj.classes_)}")
        except Exception as e:
            print(f"❌ {name} 로딩 실패: {e}")

if __name__ == "__main__":
    print("🧪 모델 및 리소스 상태 점검\n")

    check_file("model/model.pth", "모델 weight 파일")
    check_model_weights("./model.pth")

    check_label_encoders([
        ("./le_user.pkl", "User LabelEncoder"),
        ("./le_movie.pkl", "Movie LabelEncoder"),
        ("./le_region.pkl", "Region LabelEncoder")
    ])

    check_file("../data/dataset.csv", "데이터셋 CSV 파일")
