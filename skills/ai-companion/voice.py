"""
语音交互模块
支持语音识别和语音合成功能
"""
import io
import base64
import asyncio
from typing import Optional, Callable
import numpy as np

class SpeechRecognizer:
    """语音识别器"""
    
    def __init__(self, model_name: str = "base"):
        self.model_name = model_name
        self._model = None
    
    def load_model(self):
        """加载语音识别模型"""
        try:
            import whisper
            self._model = whisper.load_model(self.model_name)
            return True
        except ImportError:
            return False
        except Exception as e:
            print(f"模型加载失败: {e}")
            return False
    
    async def recognize(self, audio_data: bytes) -> str:
        """识别语音"""
        if self._model is None:
            if not self.load_model():
                return ""
        
        try:
            import whisper
            import tempfile
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio_data)
                temp_path = f.name
            
            result = await asyncio.to_thread(
                self._model.transcribe, temp_path, language="zh"
            )
            
            import os
            os.unlink(temp_path)
            
            return result.get("text", "").strip()
        except Exception as e:
            print(f"语音识别失败: {e}")
            return ""
    
    def recognize_sync(self, audio_data: bytes) -> str:
        """同步识别语音"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.recognize(audio_data))
        finally:
            loop.close()


class SpeechSynthesizer:
    """语音合成器"""
    
    def __init__(self, voice: str = "zh-CN-XiaoxiaoNeural"):
        self.voice = voice
        self._available_voices = {
            "zh-CN-XiaoxiaoNeural": "晓晓（女声）",
            "zh-CN-YunxiNeural": "云希（男声）",
            "zh-CN-XiaoyiNeural": "晓伊（女声）",
            "zh-CN-YunyangNeural": "云扬（男声）",
        }
    
    def list_voices(self) -> dict:
        """列出可用声音"""
        return self._available_voices.copy()
    
    async def synthesize(self, text: str, output_path: Optional[str] = None) -> Optional[bytes]:
        """合成语音"""
        try:
            import edge_tts
            import tempfile
            import os
            
            if output_path is None:
                output_path = tempfile.mktemp(suffix=".mp3")
            
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(output_path)
            
            with open(output_path, "rb") as f:
                audio_data = f.read()
            
            os.unlink(output_path)
            return audio_data
            
        except ImportError:
            print("请安装 edge-tts: pip install edge-tts")
            return None
        except Exception as e:
            print(f"语音合成失败: {e}")
            return None
    
    def synthesize_sync(self, text: str, output_path: Optional[str] = None) -> Optional[bytes]:
        """同步合成语音"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.synthesize(text, output_path))
        finally:
            loop.close()
    
    async def synthesize_to_file(self, text: str, output_path: str) -> bool:
        """合成语音并保存到文件"""
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(output_path)
            return True
        except Exception as e:
            print(f"语音合成失败: {e}")
            return False


class VoiceChatEngine:
    """语音对话引擎"""
    
    def __init__(self, recognizer: Optional[SpeechRecognizer] = None,
                 synthesizer: Optional[SpeechSynthesizer] = None):
        self.recognizer = recognizer or SpeechRecognizer()
        self.synthesizer = synthesizer or SpeechSynthesizer()
    
    async def process_voice_input(self, audio_data: bytes) -> str:
        """处理语音输入，返回文字"""
        return await self.recognizer.recognize(audio_data)
    
    async def generate_voice_response(self, text: str) -> Optional[bytes]:
        """生成语音响应，返回音频数据"""
        return await self.synthesizer.synthesize(text)
    
    async def voice_conversation(self, audio_data: bytes) -> tuple[str, Optional[bytes]]:
        """语音对话：输入语音，返回文字和语音响应"""
        text = await self.process_voice_input(audio_data)
        if not text:
            return "", None
        
        voice_response = await self.generate_voice_response(text)
        return text, voice_response


class AudioProcessor:
    """音频处理器"""
    
    @staticmethod
    def bytes_to_audio(audio_bytes: bytes) -> np.ndarray:
        """将字节转换为音频数组"""
        import struct
        import wave
        
        try:
            with wave.open(io.BytesIO(audio_bytes), 'rb') as wav:
                frames = wav.readframes(wav.getnframes())
                audio_data = np.frombuffer(frames, dtype=np.int16)
                return audio_data
        except Exception as e:
            print(f"音频转换失败: {e}")
            return np.array([])
    
    @staticmethod
    def audio_to_bytes(audio_data: np.ndarray, sample_rate: int = 16000) -> bytes:
        """将音频数组转换为字节"""
        import struct
        import wave
        import io
        
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(audio_data.tobytes())
        
        return buffer.getvalue()
    
    @staticmethod
    def base64_to_audio(base64_str: str) -> bytes:
        """将Base64字符串转换为音频字节"""
        try:
            return base64.b64decode(base64_str)
        except Exception as e:
            print(f"Base64解码失败: {e}")
            return b""
    
    @staticmethod
    def audio_to_base64(audio_bytes: bytes) -> str:
        """将音频字节转换为Base64字符串"""
        return base64.b64encode(audio_bytes).decode('utf-8')


class VoicePersona:
    """语音人格配置"""
    
    def __init__(self, persona_id: str, name: str, 
                 voice: str = "zh-CN-XiaoxiaoNeural"):
        self.persona_id = persona_id
        self.name = name
        self.voice = voice
        
        self.voice_settings = {
            "zh-CN-XiaoxiaoNeural": {"rate": "+0%", "volume": "+0%", "pitch": "+0Hz"},
            "zh-CN-YunxiNeural": {"rate": "+0%", "volume": "+0%", "pitch": "-5Hz"},
            "zh-CN-XiaoyiNeural": {"rate": "+10%", "volume": "+0%", "pitch": "+10Hz"},
            "zh-CN-YunyangNeural": {"rate": "-5%", "volume": "+0%", "pitch": "-10Hz"},
        }
    
    def get_voice_settings(self) -> dict:
        """获取语音设置"""
        return self.voice_settings.get(self.voice, {"rate": "+0%", "volume": "+0%", "pitch": "+0Hz"})
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "persona_id": self.persona_id,
            "name": self.name,
            "voice": self.voice,
            "voice_settings": self.get_voice_settings()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "VoicePersona":
        """从字典创建"""
        vp = cls(
            data["persona_id"],
            data["name"],
            data.get("voice", "zh-CN-XiaoxiaoNeural")
        )
        return vp


async def test_voice_functions():
    """测试语音功能"""
    print("测试语音合成...")
    synthesizer = SpeechSynthesizer()
    
    voices = synthesizer.list_voices()
    print("可用声音:")
    for voice_id, voice_name in voices.items():
        print(f"  {voice_id}: {voice_name}")
    
    print("\n测试语音合成...")
    audio = await synthesizer.synthesize("你好，这是一个语音合成测试。")
    if audio:
        print(f"语音合成成功，生成了 {len(audio)} 字节的音频")
    else:
        print("语音合成失败")
    
    print("\n测试语音识别...")
    recognizer = SpeechRecognizer()
    print("语音识别模型加载中...")
    if recognizer.load_model():
        print("模型加载成功")
    else:
        print("模型加载失败，请安装: pip install openai-whisper")


if __name__ == "__main__":
    asyncio.run(test_voice_functions())
