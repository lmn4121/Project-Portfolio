# imports
import gradio as gr
from dotenv import load_dotenv
from twin import chat, clear_history, session

load_dotenv(override=True)

CSS = """
.gradio-container {
    max-width: 880px !important;
    margin: auto !important;
}
#twin-header {
    text-align: center;
    padding: 1.25rem 0 0.5rem 0;
    border-bottom: 1px solid #2a3038;
    margin-bottom: 1rem;
}
#twin-header h1 {
    font-size: 1.75rem !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em;
    color: #e8eaed !important;
    margin-bottom: 0.35rem !important;
}
#twin-header p {
    color: #9aa0a6 !important;
    font-size: 0.95rem !important;
    margin: 0 !important;
}
#chatbot {
    border: 1px solid #2a3038 !important;
    border-radius: 12px !important;
    background: #161b22 !important;
}
/* Outer bubble only — style once, then clear nested Gradio wrappers */
#chatbot .message-row .message,
#chatbot .message-row .message-bubble,
#chatbot .message-row .bubble {
    border: 0 !important;
    box-shadow: none !important;
}
#chatbot .message-row.user-row .message,
#chatbot .message-row.user-row .message-bubble,
#chatbot .message-row.user-row .bubble,
#chatbot .message-row[data-role="user"] .message,
#chatbot .message-row[data-role="user"] .message-bubble,
#chatbot .message-row[data-role="user"] .bubble {
    background: #21262d !important;
    border: 1px solid #3d4450 !important;
    color: #e8eaed !important;
}
#chatbot .message-row.bot-row .message,
#chatbot .message-row.bot-row .message-bubble,
#chatbot .message-row.bot-row .bubble,
#chatbot .message-row[data-role="assistant"] .message,
#chatbot .message-row[data-role="assistant"] .message-bubble,
#chatbot .message-row[data-role="assistant"] .bubble {
    background: #1c2128 !important;
    border: 1px solid #30363d !important;
    color: #e8eaed !important;
}
#chatbot .message-row.bot-row .message:has(.thinking-bubble),
#chatbot .message-row.bot-row .message-bubble:has(.thinking-bubble),
#chatbot .message-row.bot-row .bubble:has(.thinking-bubble),
#chatbot .message-row[data-role="assistant"] .message:has(.thinking-bubble),
#chatbot .message-row[data-role="assistant"] .message-bubble:has(.thinking-bubble),
#chatbot .message-row[data-role="assistant"] .bubble:has(.thinking-bubble) {
    border-color: #58a6ff !important;
    box-shadow: 0 0 0 1px rgba(88, 166, 255, 0.25), 0 0 18px rgba(88, 166, 255, 0.12) !important;
}
/* Kill the nested second box Gradio wraps around text */
#chatbot .message-row .message .message,
#chatbot .message-row .message .message-bubble,
#chatbot .message-row .message .bubble,
#chatbot .message-row .message-bubble .message,
#chatbot .message-row .message-bubble .message-bubble,
#chatbot .message-row .message-bubble .bubble,
#chatbot .message-row .bubble .message,
#chatbot .message-row .bubble .message-bubble,
#chatbot .message-row .bubble .bubble,
#chatbot .message-row .message *,
#chatbot .message-row .message-bubble *,
#chatbot .message-row .bubble * {
    background: transparent !important;
    border: 0 !important;
    border-color: transparent !important;
    box-shadow: none !important;
}
#chatbot .message-row .message,
#chatbot .message-row .message-bubble,
#chatbot .message-row .bubble,
#chatbot .message-row .message *,
#chatbot .message-row .message-bubble *,
#chatbot .message-row .bubble * {
    color: #e8eaed !important;
}
.thinking-bubble {
    display: inline-flex !important;
    align-items: center;
    gap: 0.55rem;
    color: #58a6ff !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em;
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
    padding: 0 !important;
    animation: twin-pulse 1.4s ease-in-out infinite;
}
.thinking-bubble,
.thinking-bubble * {
    color: #58a6ff !important;
}
.thinking-bubble .dots {
    display: inline-flex;
    gap: 0.28rem;
}
.thinking-bubble .dots span {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #58a6ff !important;
    opacity: 0.35;
    animation: twin-dot 1.2s ease-in-out infinite;
}
.thinking-bubble .dots span:nth-child(2) { animation-delay: 0.15s; }
.thinking-bubble .dots span:nth-child(3) { animation-delay: 0.3s; }
@keyframes twin-pulse {
    0%, 100% { opacity: 0.75; }
    50% { opacity: 1; }
}
@keyframes twin-dot {
    0%, 80%, 100% { opacity: 0.3; transform: translateY(0); }
    40% { opacity: 1; transform: translateY(-2px); }
}
#msg-box textarea {
    border-radius: 10px !important;
    border-color: #2a3038 !important;
    background: #161b22 !important;
}
#send-btn, #new-chat-btn {
    border-radius: 10px !important;
    min-height: 42px;
}
#new-chat-btn {
    background: transparent !important;
    border: 1px solid #3d4450 !important;
    color: #c9d1d9 !important;
}
#new-chat-btn:hover {
    border-color: #58a6ff !important;
    color: #58a6ff !important;
}
#send-btn {
    background: #238636 !important;
    border: 1px solid #238636 !important;
    color: #ffffff !important;
}
#send-btn:hover {
    background: #2ea043 !important;
    border-color: #2ea043 !important;
}
footer { display: none !important; }
"""

THEME = gr.themes.Base(
    primary_hue="blue",
    secondary_hue="slate",
    neutral_hue="slate",
    font=gr.themes.GoogleFont("IBM Plex Sans"),
    font_mono=gr.themes.GoogleFont("IBM Plex Mono"),
).set(
    body_background_fill="#0d1117",
    body_background_fill_dark="#0d1117",
    body_text_color="#e8eaed",
    body_text_color_dark="#e8eaed",
    background_fill_primary="#0d1117",
    background_fill_primary_dark="#0d1117",
    background_fill_secondary="#161b22",
    background_fill_secondary_dark="#161b22",
    block_background_fill="#161b22",
    block_background_fill_dark="#161b22",
    block_border_color="#2a3038",
    block_border_color_dark="#2a3038",
    block_label_text_color="#9aa0a6",
    block_label_text_color_dark="#9aa0a6",
    block_title_text_color="#e8eaed",
    block_title_text_color_dark="#e8eaed",
    border_color_primary="#2a3038",
    border_color_primary_dark="#2a3038",
    input_background_fill="#161b22",
    input_background_fill_dark="#161b22",
    button_primary_background_fill="#238636",
    button_primary_background_fill_dark="#238636",
    button_primary_text_color="#ffffff",
    button_primary_text_color_dark="#ffffff",
    button_secondary_background_fill="#21262d",
    button_secondary_background_fill_dark="#21262d",
    button_secondary_text_color="#c9d1d9",
    button_secondary_text_color_dark="#c9d1d9",
)


THINKING_HTML = (
    '<div class="thinking-bubble">'
    "Thinking"
    '<span class="dots"><span></span><span></span><span></span></span>'
    "</div>"
)


async def respond(message, history):
    message = (message or "").strip()
    if not message:
        yield history, ""
        return

    history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": THINKING_HTML},
    ]
    yield history, ""

    started = False
    async for delta in chat(message, history[:-2]):
        if not started:
            history[-1]["content"] = delta
            started = True
        else:
            history[-1]["content"] += delta
        yield history, ""

    if not started:
        history[-1]["content"] = "I didn't get a response. Please try again."
        yield history, ""


async def new_chat():
    await clear_history(session)
    return [], ""


def build_app() -> gr.Blocks:
    with gr.Blocks(title="Landon Nguyen — Digital Twin", fill_height=True) as demo:
        with gr.Column(elem_id="twin-header"):
            gr.Markdown(
                "# Landon Nguyen\n"
                "Digital twin · Ask about background, skills, and experience"
            )

        chatbot = gr.Chatbot(
            elem_id="chatbot",
            height=520,
            show_label=False,
            sanitize_html=False,
            placeholder="Ask about projects, skills, coursework, or experience…",
        )

        with gr.Row():
            msg = gr.Textbox(
                elem_id="msg-box",
                placeholder="Type a message…",
                show_label=False,
                scale=6,
                autofocus=True,
                container=False,
            )
            send_btn = gr.Button("Send", elem_id="send-btn", variant="primary", scale=1)
            new_chat_btn = gr.Button(
                "New Chat", elem_id="new-chat-btn", variant="secondary", scale=1
            )

        msg.submit(respond, inputs=[msg, chatbot], outputs=[chatbot, msg])
        send_btn.click(respond, inputs=[msg, chatbot], outputs=[chatbot, msg])
        new_chat_btn.click(new_chat, outputs=[chatbot, msg])

    return demo


def main():
    demo = build_app()
    demo.launch(inbrowser=True, theme=THEME, css=CSS)


if __name__ == "__main__":
    main()
