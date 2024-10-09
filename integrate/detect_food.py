import cv2
import gradio as gr
import json
from ultralytics import YOLO
from deepdiff import DeepDiff


model = YOLO("./integrate/edit_best.pt")
def caps(cap):
    for _ in range(5):
        ret, frame = cap.read()
    return ret, frame

def capture_frame():
    # เปิดการเชื่อมต่อกับ webcam
    cap = cv2.VideoCapture(0)
    ret, frame = caps(cap)
    if not ret:
        return None
    # ปิดการเชื่อมต่อกับ webcam
    cap.release()
    # เปลี่ยนสีจาก BGR เป็น RG
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return frame

def detect_ingredients(frame):
    if frame is None:
        return json.dumps({"food": [], "state": "Haven't"})

    # แปลงภาพจาก BGR เป็น RGB
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # ปรับขนาดของภาพให้เหมาะสม (640x640)
    img_resized = img
    
    # สมมติว่า model สามารถทำงานได้และมีการใช้ตามนี้
    results = model(img_resized)

    ingredients = []
    for result in results:
        for det in result.boxes:
            cls = int(det.cls)
            label = model.names[cls]
            ingredients.append(label)

            # วาดกรอบรอบวัตถุที่ตรวจจับได้
            xyxy = det.xyxy[0].cpu().numpy().astype(int)
            cv2.rectangle(frame, (xyxy[0], xyxy[1]), (xyxy[2], xyxy[3]), (0, 255, 0), 2)
            cv2.putText(frame, label, (xyxy[0], xyxy[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # state = "Have" if len(ingredients) > 0 else "Haven't"
    json_new = {"food": ingredients}
    json_result = json.dumps(json_new)

    with open('./integrate/data.json', 'r') as openfile:
        # Reading from json file
        json_old = json.load(openfile)
    # Compare the JSON objects
    diff = DeepDiff(json_old, json_new, ignore_order=True)
    val_rem = []
    if not diff:
        print("ไม่พบความแตกต่าง:")
    else:
        print(diff)
        if 'iterable_item_removed' in diff:
            val_rem = list(diff['iterable_item_removed'].values())
            print('Have',end=' ')
            for i in val_rem:
                print(f'{i}',end=' ')
            print('remove')
        elif 'iterable_item_added' in diff:
            val_add = list(diff['iterable_item_added'].values())
            print('Have',end=' ')
            for i in val_add:
                print(f'{i}',end=' ')
            print('add')
        elif 'values_changed' in diff:
            print("มีของหายไปและเพิ่มเข้ามา")
            val = diff['values_changed'].values()
            val_add = [change['new_value'] for change in val]
            val_rem = [change['old_value'] for change in val]

            print(val_add, val_rem)
        with open("./integrate/data.json", "w") as outfile:
            outfile.write(json_result)
        print("พบความแตกต่าง:")

    return json_result, val_rem


def gradio_webcam_interface():
    frame = capture_frame()
    if frame is not None:
        json_result, val_rem = detect_ingredients(frame)
        return frame, json_result
    else:
        return None, json.dumps({"food": [], "state": "Haven't"})

interface = gr.Interface(
    fn=gradio_webcam_interface,
    inputs=None,
    outputs=[
        gr.Image(type="numpy", label="ถ่ายรูปจาก webcam"),
        gr.Textbox(label="ผลลัพธ์ JSON")
    ]
)

interface.launch()
