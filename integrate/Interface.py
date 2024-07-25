import gradio as gr

css = """

"""

with gr.Blocks() as lintech:
    gr.Markdown("<h1 style='font-size: 80px;'>LinTech<h1>")
    # gr.Markdown("What do you have now  🍽️")
    
    # with gr.Row() as first_row:
    #     quantity = gr.HTML(f"""
    #         <div style='display: flex; justify-content: space-around; align-items: center; height: 300px; width: 100%; background-color: white; border-radius: 25px; flex-wrap: wrap;'>
    #             <div style='display: flex; justify-content: space-around; align-items: center;'>
    #                 <img src="https://img.freepik.com/premium-vector/apple-isolated-white-background_114835-24882.jpg" alt="apple" style='width: 50px; heigth: auto;' />
    #                 <h3 style='color: black; margin-left: 10px'>Apple</h3>
    #             </div>
    #             <div style='display: flex; justify-content: space-around; align-items: center;'>
    #                 <img src="https://img.freepik.com/free-vector/loaf-bread-single-slice_1308-39519.jpg" alt="bread" style='width: 50px; heigth: auto;' />
    #                 <h3 style='color: black; margin-left: 10px'>Bread</h3>
    #             </div>
    #             <div style='display: flex; justify-content: space-around; align-items: center;'>
    #                 <img src="https://static.vecteezy.com/system/resources/previews/007/697/457/non_2x/a-mouth-watering-isometric-icon-of-grapes-vector.jpg" alt="grape" style='width: 50px; heigth: auto;' />
    #                 <h3 style='color: black; margin-left: 10px'>Grape</h3>
    #             </div>
    #         </div>
    #     """)
    #     camera = gr.Video()
    
    # with gr.Row() as second_row:
    #     with gr.Column() as form:
    #         gr.Dropdown(
    #             [str(i) for i in range(1, 8)], label="Planning Range", info="choose between 1 - 7 days"
    #         ),
    #         text_input = gr.Textbox(lines=2, placeholder="Fill specific food (optional)")
    #         submit_button = gr.Button("See result")
    #     with gr.Column() as res:
    #         chatbot = gr.Chatbot(height="240px")
    #         gr.Markdown("<a>see your grocery list</a> 🥗")

lintech.launch()
