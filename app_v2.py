"""
AI陪伴 V2 - 带语音交互的Web应用
"""
import gradio as gr
import json
import os
from skills.ai_companion.mobile import MobileAICompanion
from skills.ai_companion.voice import SpeechRecognizer, SpeechSynthesizer, VoiceChatEngine
import tempfile
import base64

companion = MobileAICompanion(model_id="qwen2:0.5b")
speech_recognizer = SpeechRecognizer()
speech_synthesizer = SpeechSynthesizer()
voice_engine = VoiceChatEngine(speech_recognizer, speech_synthesizer)

current_persona_id = None

def load_personas():
    personas = companion.list_personas()
    return [(p.name, p.persona_id) for p in personas]

def load_voices():
    return [(f"{name} ({vid})", vid) for vid, name in speech_synthesizer.list_voices().items()]

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
    global current_persona_id
    current_persona_id = persona_id
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

def process_voice(audio, persona_id):
    """处理语音输入"""
    if audio is None or not persona_id:
        return None, gr.update()
    
    try:
        import numpy as np
        import wave
        
        audio_data = audio
        if isinstance(audio, tuple):
            sample_rate, audio_data = audio
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            if isinstance(audio_data, np.ndarray):
                audio_int16 = (audio_data * 32767).astype(np.int16)
                with wave.open(f.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate or 16000)
                    wav_file.writeframes(audio_int16.tobytes())
            else:
                f.write(audio_data)
            temp_path = f.name
        
        with open(temp_path, "rb") as f:
            audio_bytes = f.read()
        
        import os
        os.unlink(temp_path)
        
        text = speech_recognizer.recognize_sync(audio_bytes)
        
        if not text:
            return None, gr.update(value="无法识别语音")
        
        response = companion.chat(persona_id, text)
        
        if response["status"] == "success":
            voice_audio = speech_synthesizer.synthesize_sync(response["response"])
            
            if voice_audio:
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    f.write(voice_audio)
                    temp_audio_path = f.name
                
                return temp_audio_path, gr.update(value=f"你说: {text}\nAI回复: {response['response']}")
            else:
                return None, gr.update(value=f"你说: {text}\nAI回复: {response['response']}")
        else:
            return None, gr.update(value=f"错误: {response['message']}")
            
    except Exception as e:
        return None, gr.update(value=f"处理失败: {str(e)}")

def select_voice(voice_id):
    """选择语音"""
    speech_synthesizer.voice = voice_id
    return gr.update(value=f"已切换到语音: {voice_id}")

def clear_chat():
    return []

def set_model(model_id):
    if model_id:
        result = companion.set_model(model_id)
        return gr.update(value=f"当前模型: {result.get('message', '切换失败')}")
    return gr.update(value="")

def download_model(model_id):
    if model_id:
        result = companion.download_model(model_id)
        return gr.update(value=result["message"])
    return gr.update(value="")

def get_available_models():
    models = companion.get_available_models()
    return [(f"{m['name']} ({m['size']}, {m['memory_req']})", m['id']) for m in models]

with gr.Blocks(title="AI陪伴 V2 - 语音交互", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 💝 AI陪伴 V2 - 语音交互版")
    gr.Markdown("与思念的人进行温暖对话，支持语音输入输出")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## 👤 人格管理")
            
            persona_dropdown = gr.Dropdown(
                choices=load_personas(),
                label="选择人格",
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
                create_btn = gr.Button("创建", variant="primary")
                create_status = gr.Textbox(label="创建状态", visible=False)
            
            persona_dropdown.change(select_persona, [persona_dropdown], [persona_status])
            create_btn.click(
                create_persona,
                [new_name, new_desc],
                [persona_dropdown, new_name, create_status, persona_status]
            )
        
        with gr.Column(scale=2):
            gr.Markdown("## 💬 文字对话")
            
            chatbot = gr.Chatbot(
                label="对话",
                height=300,
                bubble_full_width=False
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
    
    with gr.Accordion("🎤 语音交互", open=True):
        gr.Markdown("点击录音按钮说话，AI会语音回复你")
        
        with gr.Row():
            voice_dropdown = gr.Dropdown(
                choices=load_voices(),
                label="选择声音",
                value="zh-CN-XiaoxiaoNeural"
            )
            voice_status = gr.Textbox(
                label="语音状态",
                interactive=False,
                lines=1
            )
        
        audio_input = gr.Audio(
            label="🎙️ 点击录音或上传音频",
            type="numpy"
        )
        
        voice_output = gr.Audio(
            label="🔊 AI语音回复",
            type="filepath"
        )
        
        process_btn = gr.Button("🎤 处理语音", variant="primary")
        
        voice_dropdown.change(select_voice, [voice_dropdown], [voice_status])
        process_btn.click(
            process_voice,
            [audio_input, persona_dropdown],
            [voice_output, voice_status]
        )
    
    with gr.Accordion("⚙️ 模型设置", open=False):
        gr.Markdown("选择适合您设备的模型（手机建议选择小模型）")
        
        model_dropdown = gr.Dropdown(
            choices=get_available_models(),
            label="选择模型",
            value="qwen2:0.5b"
        )
        
        model_status = gr.Textbox(label="模型状态", interactive=False)
        
        with gr.Row():
            select_model_btn = gr.Button("应用模型")
            download_model_btn = gr.Button("下载模型")
        
        select_model_btn.click(set_model, [model_dropdown], [model_status])
        download_model_btn.click(download_model, [model_dropdown], [model_status])
        
        gr.Markdown("""
        **模型选择建议:**
        
        | 模型 | 大小 | 内存需求 | 适合设备 |
        |------|------|----------|----------|
        | Qwen2-0.5B | 0.5B | 2GB | 旧手机 |
        | Gemma-2B | 2B | 3GB | 中档手机 |
        | Qwen2-1.5B | 1.5B | 3GB | 中档手机 |
        | Mistral-7B-Q4 | 7B | 5GB | 高端手机 |
        """)
    
    gr.Markdown("---")
    gr.Markdown("*让爱与记忆永不消逝 ❤️* | V2 新增语音交互功能")

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True
    )
