import os
from dotenv import dotenv_values

import gradio as gr
from model import model_Grocery, model_Waste
from integrate.detect_f import gradio_webcam_interface

config = dotenv_values(".env")

os.environ["OPENAI_API_KEY"] = config["openai_api"]
os.environ["ANTHROPIC_API_KEY"] = config["ANTHROPIC_API_KEY"]

def query_Plan(numSena, duration, food, menu, totalMeals):
    model_plan_chain = model_Grocery(numSena)
    groceryList_path = './groceryList/groceryList.md'
    if os.path.exists(groceryList_path):
        os.remove(groceryList_path)
    print("menu", menu)
    if duration != None or duration != '' or duration != " ":
        question_format = f"""
        From My Family behavior please help me to plan what I need to buy for my family. I will give you information from below please use this to apply your result.\n

        This is my optional that I provide:
            This is my duration that I want, {duration} Day.\n 
            And In my fridge nows have {food} (if in my fridge have a food please don't suggest that I have but please plan a menu for clear a food that leftover).\n 
            Specific menu is {menu} (If specific menu is None you can skip it).\n
            Specific meals per one day: {totalMeals} (If specific meals is None default is Three Meals)\n
        """
    else:
        question_format = f"""
        From My Family behavior please help me to plan what I need to buy for my family. I will give you information from below please use this to apply your result.\n

        This is my optional that I provide:
            This is my duration that I want, 7 Day.\n 
            And In my fridge nows have {food} (if in my fridge have a food please don't suggest that I have but please plan a menu for clear a food that leftover).\n 
            Specific menu is {menu} (If specific menu is None you can skip it).\n
            Specific meals per one day: {totalMeals} (If specific meals is None default is Three Meals)\n
        """
    
    return model_plan_chain, question_format

def query_Waste(waste):
    model_Waste_chain = model_Waste()
    question = f"This is the object that the user takes out of the refrigerator: {waste}. Can this {waste} be solds (Price (THB) / Kg), and how to make it most useful for selling in Thai Bath. But if you can't sell it, how to make it most useful?"
    return model_Waste_chain, question

def ui_():
    with gr.Blocks() as demo:
        
        def user(user_msg, history):
            print(user_msg)
            history = history + [(user_msg, None)]
            return history, "" 
        
        def plan_bot(history, duration, scenario, food, meals):
                menu = history[-1][0]
                if any(word in menu for word in ['python', 'java']):
                    print("OK")
                    history[-1][1] = "I apologize, but according to the rules provided, I cannot assist with writing Python code or anything related to coding. My role is to help plan meals and provide a grocery list based on the given context and requirements. Let's move forward with that instead."
                    words = history[-1][1].split()
                    for chunk in words:
                        print(chunk, end="", flush=True)
                        history[-1][1] += chunk
                        yield history
                else:
                    # frame, food, waste = gradio_webcam_interface()
                
                    res, question_template = query_Plan(scenario, duration, food, menu, meals)
                    history[-1][1] = ""
                    question = question_template 

                    groceryList_path = './groceryList/groceryList.md'
                    for chunk in res.stream(question):
                        print(chunk, end="", flush=True)
                        history[-1][1] += chunk
                        yield history
                        with open(groceryList_path, 'a') as file:
                            file.write(chunk)
                    
                return history
        
        def waste_bot(waste):
            # _, _, waste = gradio_webcam_interface()
            res, question = query_Waste(waste)
            if len(waste) != 0:
                print(waste)
                output = ""
                for chunk in res.stream(question):
                    print(chunk, end="", flush=True)
                    output += chunk
                    yield output
            else:
                return "Nothing to pick it out"

        chatbot = gr.Chatbot(elem_id="chatbot-container", show_copy_button=True)
        markdown = gr.Markdown("")
        current_food = gr.HTML("")
        result = gr.HTML("", visible=False)
        remove = gr.HTML("", visible=False)
        duration = gr.Dropdown([str(i) for i in range(1, 8)], label="Planning Range", info="choose between 1 - 7 days")
        total_meals = gr.CheckboxGroup(["Breakfast", "Lunch", "Dinner"], label="How many meals", info="in one day")
        scenario = gr.Radio(["1", "2", "3"], label="Examples Scenario", info="depends on their behaviors")
        msg = gr.Textbox(lines=2, label="Fill specific food", placeholder="*optional")
        
        with gr.Row() as button_group:
            generate = gr.Button("Start Plan 🥗")
            camera_cap = gr.Button("Close Fridge")
            clear = gr.Button("Clear")
        
        # Planer Event
        # msg.submit(user, [msg, chatbot], [chatbot, msg], queue=False).then(plan_bot, chatbot, chatbot)
        # generate.click(user, [msg, chatbot], [chatbot, msg], queue=False).then(plan_bot, [chatbot, duration, scenario], chatbot)
        generate.click(
            fn=gradio_webcam_interface,
            inputs=None,
            outputs=[result, current_food]
        ).then(
            fn=user,
            inputs=[msg, chatbot],
            outputs=[chatbot, msg]
        ).then(
            fn=plan_bot,
            inputs=[chatbot, duration, scenario, result, total_meals],
            outputs=chatbot
        )
        
        clear.click(lambda: None, None, chatbot, queue=False)
        
        # Waste Event
        camera_cap.click(
            fn=gradio_webcam_interface,
            inputs=None,
            outputs=[result, current_food, remove]
        ).then(
            fn=waste_bot,
            inputs=[remove],
            outputs=markdown
        )
        
    demo.launch()
if __name__ == "__main__":
    # Final Main.py
    # duration = 2
    ui_()
