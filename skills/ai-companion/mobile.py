from typing import Dict, List, Optional, Any
import json
import os
import subprocess

class TinyModelManager:
    def __init__(self, model_dir: str = "./models/tiny"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        self.available_models = {
            "phi2": {
                "name": "Phi-2",
                "size": "2.7B",
                "quantized": True,
                "memory_req": "4GB",
                "provider": "ollama",
                "model_name": "phi2:latest"
            },
            "qwen2:0.5b": {
                "name": "Qwen2-0.5B",
                "size": "0.5B",
                "quantized": True,
                "memory_req": "2GB",
                "provider": "ollama",
                "model_name": "qwen2:0.5b"
            },
            "qwen2:1.5b": {
                "name": "Qwen2-1.5B",
                "size": "1.5B",
                "quantized": True,
                "memory_req": "3GB",
                "provider": "ollama",
                "model_name": "qwen2:1.5b"
            },
            "mistral:7b-instruct-v0.3-q4_K_M": {
                "name": "Mistral-7B-Q4",
                "size": "7B (4-bit)",
                "quantized": True,
                "memory_req": "5GB",
                "provider": "ollama",
                "model_name": "mistral:7b-instruct-v0.3-q4_K_M"
            },
            "llama3.1:8b-instruct-q4_K_M": {
                "name": "Llama3.1-8B-Q4",
                "size": "8B (4-bit)",
                "quantized": True,
                "memory_req": "6GB",
                "provider": "ollama",
                "model_name": "llama3.1:8b-instruct-q4_K_M"
            },
            "gemma:2b": {
                "name": "Gemma-2B",
                "size": "2B",
                "quantized": True,
                "memory_req": "3GB",
                "provider": "ollama",
                "model_name": "gemma:2b"
            }
        }

    def list_models(self) -> List[Dict]:
        return [{"id": k, **v} for k, v in self.available_models.items()]

    def get_model_info(self, model_id: str) -> Optional[Dict]:
        return self.available_models.get(model_id)

    def download_model(self, model_id: str) -> Dict:
        model_info = self.get_model_info(model_id)
        if not model_info:
            return {"status": "error", "message": f"模型 {model_id} 不存在"}

        try:
            result = subprocess.run(
                ["ollama", "pull", model_info["model_name"]],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "message": f"模型 {model_info['name']} 下载成功",
                    "model_id": model_id,
                    "model_name": model_info["model_name"]
                }
            else:
                return {
                    "status": "error",
                    "message": f"下载失败: {result.stderr}"
                }
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "下载超时"}
        except FileNotFoundError:
            return {"status": "error", "message": "Ollama 未安装"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def suggest_model(self, memory_available_gb: int) -> str:
        sorted_models = sorted(
            self.available_models.items(),
            key=lambda x: int(x[1]["memory_req"].replace("GB", ""))
        )
        
        for model_id, info in sorted_models:
            req_gb = int(info["memory_req"].replace("GB", ""))
            if req_gb <= memory_available_gb:
                return model_id
        
        return list(self.available_models.keys())[0]

class MobileChatEngine:
    def __init__(self, model_id: str = "qwen2:0.5b"):
        self.model_id = model_id
        self.model_manager = TinyModelManager()
        self.conversations: Dict[str, List[Dict]] = {}

    def set_model(self, model_id: str):
        if model_id in self.model_manager.available_models:
            self.model_id = model_id
            return {"status": "success", "message": f"已切换到模型: {model_id}"}
        return {"status": "error", "message": f"模型 {model_id} 不可用"}

    def generate_prompt(self, persona_name: str, persona_desc: str, 
                       traits: Dict, message: str) -> str:
        traits_str = ", ".join([f"{k}: {v}" for k, v in traits.items()])
        prompt = f"""
你现在是{persona_name}，请用{persona_name}的身份和语气回答问题。

{persona_name}的描述：{persona_desc}

{persona_name}的性格特点：{traits_str}

请用自然、亲切、简短的方式回复，保持角色一致性。

用户说：{message}

你的回复：
"""
        return prompt.strip()

    def chat(self, persona_name: str, persona_desc: str, traits: Dict,
             message: str, conversation_id: str = "default") -> Dict:
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []

        self.conversations[conversation_id].append({
            "role": "user", 
            "content": message
        })

        prompt = self.generate_prompt(persona_name, persona_desc, traits, message)
        
        model_info = self.model_manager.get_model_info(self.model_id)
        if not model_info:
            return {
                "status": "error",
                "message": "模型未配置"
            }

        try:
            import ollama
            response = ollama.chat(
                model=model_info["model_name"],
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": 0.7,
                    "max_tokens": 512,
                    "top_p": 0.9
                }
            )
            
            reply = response["message"]["content"]
            self.conversations[conversation_id].append({
                "role": "assistant",
                "content": reply
            })

            return {
                "status": "success",
                "response": reply,
                "model": self.model_id,
                "conversation_id": conversation_id
            }
        except ImportError:
            return {
                "status": "error",
                "message": "请安装 ollama 库: pip install ollama"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"模型调用失败: {str(e)}"
            }

    def get_conversation(self, conversation_id: str) -> List[Dict]:
        return self.conversations.get(conversation_id, [])

    def clear_conversation(self, conversation_id: str):
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            return {"status": "success", "message": "会话已清除"}
        return {"status": "error", "message": "会话不存在"}

class MobilePersona:
    def __init__(self, persona_id: str, name: str, description: str = ""):
        self.persona_id = persona_id
        self.name = name
        self.description = description
        self.traits: Dict[str, float] = {}
        self.avatar: Optional[str] = None
        self.voice_enabled = False

    def add_trait(self, trait: str, value: float):
        self.traits[trait] = min(1.0, max(0.0, value))

    def to_dict(self):
        return {
            "persona_id": self.persona_id,
            "name": self.name,
            "description": self.description,
            "traits": self.traits,
            "avatar": self.avatar,
            "voice_enabled": self.voice_enabled
        }

    @classmethod
    def from_dict(cls, data: Dict):
        persona = cls(data["persona_id"], data["name"], data.get("description", ""))
        persona.traits = data.get("traits", {})
        persona.avatar = data.get("avatar")
        persona.voice_enabled = data.get("voice_enabled", False)
        return persona

class MobilePersonaManager:
    def __init__(self, storage_path: str = "./data/mobile_personas"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

    def create_persona(self, name: str, description: str = "") -> MobilePersona:
        persona_id = name.lower().replace(" ", "_")
        persona = MobilePersona(persona_id, name, description)
        self._save_persona(persona)
        return persona

    def load_persona(self, persona_id: str) -> Optional[MobilePersona]:
        file_path = os.path.join(self.storage_path, f"{persona_id}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return MobilePersona.from_dict(data)
        return None

    def _save_persona(self, persona: MobilePersona):
        file_path = os.path.join(self.storage_path, f"{persona.persona_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(persona.to_dict(), f, ensure_ascii=False, indent=2)

    def list_personas(self) -> List[MobilePersona]:
        personas = []
        for filename in os.listdir(self.storage_path):
            if filename.endswith(".json"):
                persona_id = filename[:-5]
                persona = self.load_persona(persona_id)
                if persona:
                    personas.append(persona)
        return personas

    def delete_persona(self, persona_id: str):
        file_path = os.path.join(self.storage_path, f"{persona_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)

class MobileAICompanion:
    def __init__(self, model_id: str = "qwen2:0.5b"):
        self.persona_manager = MobilePersonaManager()
        self.chat_engine = MobileChatEngine(model_id)

    def create_persona(self, name: str, description: str = "") -> MobilePersona:
        return self.persona_manager.create_persona(name, description)

    def load_persona(self, persona_id: str) -> Optional[MobilePersona]:
        return self.persona_manager.load_persona(persona_id)

    def list_personas(self) -> List[MobilePersona]:
        return self.persona_manager.list_personas()

    def chat(self, persona_id: str, message: str, 
             conversation_id: str = "default") -> Dict:
        persona = self.persona_manager.load_persona(persona_id)
        if not persona:
            return {"status": "error", "message": f"未找到人格档案: {persona_id}"}
        
        return self.chat_engine.chat(
            persona.name,
            persona.description,
            persona.traits,
            message,
            conversation_id
        )

    def set_model(self, model_id: str) -> Dict:
        return self.chat_engine.set_model(model_id)

    def get_available_models(self) -> List[Dict]:
        return self.chat_engine.model_manager.list_models()

    def suggest_model(self, memory_gb: int) -> str:
        return self.chat_engine.model_manager.suggest_model(memory_gb)

    def download_model(self, model_id: str) -> Dict:
        return self.chat_engine.model_manager.download_model(model_id)

if __name__ == "__main__":
    companion = MobileAICompanion(model_id="qwen2:0.5b")
    
    print("可用模型:")
    for model in companion.get_available_models():
        print(f"- {model['id']}: {model['name']} ({model['size']}, 需要 {model['memory_req']})")
    
    grandma = companion.create_persona(
        name="奶奶",
        description="一位温柔善良的老奶奶，喜欢讲故事"
    )
    grandma.add_trait("温柔", 0.9)
    grandma.add_trait("耐心", 0.85)
    companion.persona_manager._save_persona(grandma)
    
    print("\n开始对话（手机模式）...")
    response = companion.chat("奶奶", "奶奶，我想你了")
    print(f"奶奶: {response.get('response', '无法获取回复')}")