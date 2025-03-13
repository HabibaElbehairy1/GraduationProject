import os
from PIL import Image
import torchvision.transforms.functional as TF
import numpy as np
import torch
import pandas as pd
from . import CNN  # في حال كنت داخل Django App


# الحصول على المسار الحالي للمجلد الذي يحتوي على هذا الملف
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# تحميل بيانات الأمراض والمكملات
disease_info = pd.read_csv(os.path.join(BASE_DIR, "disease_info.csv"), encoding="cp1252")
supplement_info = pd.read_csv(os.path.join(BASE_DIR, "supplement_info.csv"), encoding="cp1252")
care_guide = pd.read_csv(os.path.join(BASE_DIR, "care_guide.csv"), encoding="cp1252")


# تحميل نموذج CNN
model_path = os.path.join(BASE_DIR, "plant_disease_model_1_latest.pt")
model = CNN.CNN(39)
model.load_state_dict(torch.load(model_path, map_location=torch.device("cpu")))
model.eval()

def predict_disease(image_path):
    """يتنبأ بمرض النبات من صورة."""
    image = Image.open(image_path).resize((224, 224))
    input_data = TF.to_tensor(image).unsqueeze(0)

    output = model(input_data)
    pred_index = np.argmax(output.detach().numpy())

    # إرجاع تفاصيل المرض والعلاج
    return {
        "disease_name": disease_info.loc[pred_index, "disease_name"],
        "description": disease_info.loc[pred_index, "description"],
        "care_guide": care_guide.loc[pred_index, "care_guide"],
        "prevention_steps": disease_info.loc[pred_index, "Possible Steps"],
        "supplement_name": supplement_info.loc[pred_index, "supplement name"],
        # "supplement_image_url": supplement_info.loc[pred_index, "supplement image"],
        # "supplement_buy_link": supplement_info.loc[pred_index, "buy link"],
    }
