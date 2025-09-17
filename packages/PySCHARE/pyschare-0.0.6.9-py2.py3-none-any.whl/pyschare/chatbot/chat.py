# import time
import markdown2
from IPython.display import HTML, display
import ipywidgets as widgets
from pyschare.chatbot.rag_response import generate_response

# ======== Styling ========
def get_custom_css():
    return """
    <style>
        .header {
            display: flex; 
            flex-direction:column;
            justify-content: center; 
            align-items: center; 
            background: #F8F8F8;
            border-radius: 12px;
            margin-bottom:  10px;
        }
        .header p {
            font-size: 14px;
            color: #282828;
            letter-spacing: 2px;
            font-weight: bold;
        }
        .note {
            border-left: 8px solid #B2BEB5;
            padding: 12px 30px;
            margin-top: 5px;
            border-bottom-left-radius: 12px;
        }
        .chat-container {
            display: flex;
            flex-direction:row;
            align-items: center;
            gap:10px;
        }
        .schare-ai {
            margin-right: 5px;
            font-weight: bold;
        }
        .chat-response {
            background: white;
            padding: 1em;
            border-radius: 12px;
            border: 1px solid black;
            color: black;
            font-size: 15px;
            font-family: 'Fira Code', monospace;
            margin-top: 10px;
            line-height: 1.5;
            width: 80% !important;
        }
        .user-message {
            font-size: 15px;
            color: #333;
            margin: 10px;
            text-align: right;
            padding-top: 10px;
        }
        .user-bubble {
            border: 1px solid #0066b2;
            border-radius: 12px;
            padding: 1em;
            margin: 0px 15px 0px 10px;
            display: inline-block;
            background-color: #f0f8ff;
            font-family: 'Fira Code', monospace;
        }
        .user-label {
            color: #0066b2;
            font-weight: bold;
        }
        .textarea-box {
            width:80%;
            height:100px;
            margin-left:90px;
            margin-top:20px;
        }
        .textarea-box textarea {
            background:#F8F8F8;
            border: 1px solid #dcdcdc;
            border-radius: 12px;
            box-shadow: 0 0 7px rgba(0, 0, 0, 0.1);
            padding: 12px;
            font-size: 14px;
            resize: vertical;
            outline: none !important;
            transition: box-shadow 0.2s ease;
        }
        .textarea-box textarea:focus {
            box-shadow: 0 0 7px rgba(0, 0, 0, 0.1);
            border-color: #a0a0a0;
        }
        .button {
            width: 15%;
            height: 40px;
            color: white;
            font-weight: bold;
            background:#0066b2;
            margin: 20px auto;
            border-radius: 8px;
        }

        .chat-response.loading {
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: shimmer 2.0s infinite;
            min-height: 40px; /* ensures visible box even if empty */
            border: 1px solid #ccc;
            border-radius: 12px;
        }

        @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
    </style>
    """


# ======== Response Formatting ========
def format_response(response_text):
    html_text = markdown2.markdown(response_text, extras=["break-on-newline"])
    return f"""
    <div class="chat-container">
        <span class="schare-ai">SCHARE AI</span>
        <div class="chat-response">{html_text}</div>
    </div>
    """

def format_user_question(user_question):
    html_text = user_question.replace("\n", "<br>")
    return f"""
    <div class="user-message">
        <span class="user-bubble">{html_text}</span>
        <b class="user-label">You</b> 
    </div>
    """

def header_text():
    return f"""
    <div class="header">
        <h3>💬 SCHARE-AI</h3>
        <p>A Smart Conversational Helper</p>
        <div class="note">
            Once I identify the dataset name, please navigate to the <strong>DATA</strong> tab in the workspace and search for that dataset.  
            Similarly, when I provide the notebook name, go to the <strong>ANALYSIS</strong> tab and locate the corresponding notebook there.
        </div>
    </div>
    <div class="chat-container">
        <span class="schare-ai">SCHARE AI</span>
        <div class="chat-response">👋 Hi! I'm SCHARE-AI, how can I help you today?</div>
    </div>
    """


# ======== Main UI Launch Function ========
def rag():
    input_box = widgets.Textarea(
        placeholder='Type your question here, then press Enter or click Send',
        layout=widgets.Layout(width='80%', height='100px', margin='20px 0 0 90px'),
    )
    input_box.add_class("textarea-box")

    send_button = widgets.Button(description="Send")
    send_button.add_class("button")

    output_box = widgets.Output()

    def process_user_input(user_question):
        if not user_question:
            return

        input_box.value = ""  # Clear input
        with output_box:
            display(HTML(format_user_question(user_question)))

            # Adding this for the animated output box first
            ai_widget = widgets.HTML(
                value="""
                <div class="chat-container">
                    <span class="schare-ai">SCHARE AI</span>
                    <div class="chat-response loading"></div>
                </div>
                """
            )
            
            display(ai_widget)


            try:
                response = generate_response(user_question)
                # display(HTML(format_response(response)))
                formatted_response = format_response(response)

                # added this new
                ai_widget.value = f"""
                    <div>{formatted_response}</div>
                    """
                # ---
            except Exception as e:
                # display(HTML(format_response(f"<span style='color:red;'>Error: {e}</span>")))
                ai_widget.value = f"""
                    <div style="color:red;">Error: {e}</div>
                    """

    def on_textarea_keypress(change):
        if change['name'] == 'value':
            if change['new'].endswith('\n') and not change['new'].endswith('\n\n'):
                process_user_input(change['new'].strip())

    send_button.on_click(lambda _: process_user_input(input_box.value.strip()))
    input_box.observe(on_textarea_keypress, names='value')

    display(HTML(get_custom_css()))
    display(widgets.VBox([
        widgets.HTML(header_text()),
        output_box,
        input_box,
        send_button
    ]))