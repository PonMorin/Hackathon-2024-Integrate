import cv2
import gradio as gr
import json
from ultralytics import YOLO
from deepdiff import DeepDiff
from food_list import food_list

DEBUG = 0

model = YOLO("./integrate/edit_best.pt")


def capture_frame():
    # เปิดการเชื่อมต่อกับ webcam
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if not ret:
        return None
    # ปิดการเชื่อมต่อกับ webcam
    cap.release()
    # เปลี่ยนสีจาก BGR เป็น RG
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return frame

def detect_ingredients(frame):

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
    if DEBUG:print(json_new)
    json_result = json.dumps(json_new)

    with open('./integrate/data.json', 'r') as openfile:
        # Reading from json file
        json_old = json.load(openfile)
    # Compare the JSON objects
    diff = DeepDiff(json_old, json_new, ignore_order=True)
    val_rem = []
    if not diff:
        if DEBUG: print("ไม่พบความแตกต่าง")
    else:
        # if DEBUG:print(diff)
        if DEBUG: print("พบความแตกต่าง")

        if 'iterable_item_removed' in diff:
            val_rem = list(diff['iterable_item_removed'].values())

            if DEBUG:
                print('มี',end=' ')
                for i in val_rem:
                    print(f'{i}',end=' ')
                print('หายไป')

        elif 'iterable_item_added' in diff:
            val_add = list(diff['iterable_item_added'].values())

            if DEBUG:
                print('มี',end=' ')
                for i in val_add:
                    print(f'{i}',end=' ')
                print('เพิ่มเข้ามา')

        elif 'values_changed' in diff:

            val = diff['values_changed'].values()
            val_add = [change['new_value'] for change in val]
            val_rem = [change['old_value'] for change in val]

            if DEBUG: print(f'มี {val_add}เพิ่มเข้ามา \nและ {val_rem} หายไป')
        with open("./integrate/data.json", "w") as outfile:
            outfile.write(json_result)

    return json_result, val_rem

def json_transform(json_result):
    data = json.loads(json_result)
    value = data["food"]
    return value


def gradio_webcam_interface(scenario, duration, food_chose):
    frame = capture_frame()
    
    if frame is not None:
        json_result, val_rem = detect_ingredients(frame)
        detected_result = json_transform(json_result)
        
        template = ""
        for i in detected_result:
            print(food_list[i]["name"], food_list[i]["imgPath"])
            template += f"""
                <div style='display: flex; justify-content: space-around; align-items: center;'>
                    <img src="{food_list[i]["imgPath"]}" alt="{food_list[i]["name"]}" style='width: 100px; heigth: auto;' />
                    <h1 style='color: black; margin-left: 10px'>{food_list[i]["name"]}</h1>
                </div>
            """
        
        html_result = f"""
            <div style='display: flex; justify-content: space-around; align-items: center; height: 150px; width: 100%; background-color: white; border-radius: 25px; flex-wrap: wrap;'>
                {template}
            </div>
            """
        return html_result
    else:
        return json.dumps({"food": [], "state": "Haven't"})

with gr.Blocks() as interface:
    gr.Markdown("<h1 style='font-size: 80px;'>LinTech<h1>")
    
    current_food = gr.HTML("")
    chatbot = gr.Chatbot()
    
    duration = gr.Dropdown([str(i) for i in range(1, 8)], label="Planning Range", info="choose between 1 - 7 days")
    food_chose = gr.Textbox(lines=2, placeholder="Fill specific food (optional)")
    
    scenario = gr.Radio(["1", "2", "3"], label="Examples Scenario", info="depends on their behaviors")
    generate_button = gr.Button("Submit 🥗")
    
    generate_button.click(
        fn=gradio_webcam_interface,
        inputs=[scenario, duration, food_chose],
        outputs=[current_food],
    )
    
if __name__ == "__main__":
    interface.launch()
