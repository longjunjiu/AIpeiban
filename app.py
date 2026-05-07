import gradio as gr
import json
import os
from mobile import MobileAICompanion

companion = MobileAICompanion()

def load_personas():
    personas = companion.list_personas()
    return [(p.name, p.persona_id) for p in personas]

def load_models():
    models = companion.get_available_models()
    return [(f"{m['name']} ({m['size']}, {m['memory_req']})", m['id']) for m in models]

def create_persona(name, description):
    if not name.strip():
        return gr.update(), gr.update(), gr.update(visible=True, value="请输入人格名称"), gr.update()
    
    companion.create_persona(name.strip(), description.strip())
    return (
        gr.update(choices=load_personas()),
        gr.update(value=""),
        gr.update(visible=False, value=""),
        gr.update(value=f"人格「{name}」创建成功！")
    )

def select_persona(persona_id):
    if persona_id:
        persona = companion.load_persona(persona_id)
        if persona:
            return gr.update(value=f"已选择: {persona.name}")
    return gr.update(value="")

def send_message(message, persona_id, history):
    if not message.strip() or not persona_id:
        return gr.update(value=""), history
    
    response = companion.chat(persona_id, message.strip())
    
    if response["status"] == "success":
        history.append((message.strip(), response["response"]))
    else:
        history.append((message.strip(), f"错误: {response['message']}"))
    
    return gr.update(value=""), history

def select_model(model_id):
    if model_id:
        result = companion.set_model(model_id)
        return gr.update(value=f"当前模型: {result.get('message', '切换失败')}")
    return gr.update(value="")

def download_selected_model(model_id):
    if model_id:
        result = companion.download_model(model_id)
        return gr.update(value=result["message"])
    return gr.update(value="")

def clear_chat():
    return []

with gr.Blocks(title="AI陪伴", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 💝 AI陪伴")
    gr.Markdown("与思念的人进行温暖的对话")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## 👤 选择人格")
            
            persona_dropdown = gr.Dropdown(
                choices=load_personas(),
                label="选择已有人格",
                value=None
            )
            
            persona_status = gr.Textbox(
                label="状态",
                interactive=False,
                lines=1
            )
            
            with gr.Accordion("➕ 创建新人格", open=False):
                new_name = gr.Textbox(label="人格名称", placeholder="输入名字...")
                new_desc = gr.Textbox(label="描述", placeholder="描述这个人的特点...", lines=2)
                create_btn = gr.Button("创建")
                create_status = gr.Textbox(label="创建状态", visible=False)
            
            persona_dropdown.change(select_persona, [persona_dropdown], [persona_status])
            create_btn.click(
                create_persona,
                [new_name, new_desc],
                [persona_dropdown, new_name, create_status, persona_status]
            )
        
        with gr.Column(scale=2):
            gr.Markdown("## 💬 对话")
            
            chatbot = gr.Chatbot(
                label="对话",
                height=400,
                bubble_full_width=False,
                avatar_images=(None, "https://neeko-copilot.bytedance.net/api/text_to_image?prompt=warm%20friendly%20avatar%20face&image_size=square")
            )
            
            msg = gr.Textbox(
                label="输入消息",
                placeholder="输入你想说的话...",
                lines=2
            )
            
            with gr.Row():
                send_btn = gr.Button("发送", variant="primary")
                clear_btn = gr.Button("清空")
            
            send_btn.click(
                send_message,
                [msg, persona_dropdown, chatbot],
                [msg, chatbot]
            )
            msg.submit(
                send_message,
                [msg, persona_dropdown, chatbot],
                [msg, chatbot]
            )
            clear_btn.click(clear_chat, [], [chatbot])
    
    with gr.Accordion("⚙️ 模型设置", open=False):
        gr.Markdown("选择适合您设备的模型（手机建议选择小模型）")
        
        model_dropdown = gr.Dropdown(
            choices=load_models(),
            label="选择模型",
            value="qwen2:0.5b"
        )
        
        model_status = gr.Textbox(label="模型状态", interactive=False)
        
        with gr.Row():
            select_model_btn = gr.Button("应用模型")
            download_model_btn = gr.Button("下载模型")
        
        select_model_btn.click(select_model, [model_dropdown], [model_status])
        download_model_btn.click(download_selected_model, [model_dropdown], [model_status])
        
        gr.Markdown("""
        **模型选择建议:**
        
        | 模型 | 大小 | 内存需求 | 适合设备 |
        |------|------|----------|----------|
        | Qwen2-0.5B | 0.5B | 2GB | 旧手机 |
        | Gemma-2B | 2B | 3GB | 中档手机 |
        | Qwen2-1.5B | 1.5B | 3GB | 中档手机 |
        | Phi-2 | 2.7B | 4GB | 高端手机 |
        | Mistral-7B-Q4 | 7B | 5GB | 手机/平板 |
        """)
    
    gr.Markdown("---")
    gr.Markdown("*让爱与记忆永不消逝 ❤️*")

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )