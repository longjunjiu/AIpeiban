from typing import Dict, List, Optional
import json
import os

class Persona:
    def __init__(self, persona_id: str, name: str, description: str = ""):
        self.persona_id = persona_id
        self.name = name
        self.description = description
        self.voice_samples: List[str] = []
        self.text_samples: List[str] = []
        self.personality_traits: Dict[str, float] = {}
        self.memory: List[Dict] = []
        self.distilled_model_path: Optional[str] = None

    def add_voice_sample(self, file_path: str):
        if os.path.exists(file_path):
            self.voice_samples.append(file_path)

    def add_text_sample(self, file_path: str):
        if os.path.exists(file_path):
            self.text_samples.append(file_path)

    def add_personality_trait(self, trait: str, value: float):
        self.personality_traits[trait] = value

    def to_dict(self):
        return {
            "persona_id": self.persona_id,
            "name": self.name,
            "description": self.description,
            "voice_samples": self.voice_samples,
            "text_samples": self.text_samples,
            "personality_traits": self.personality_traits,
            "memory": self.memory,
            "distilled_model_path": self.distilled_model_path
        }

    @classmethod
    def from_dict(cls, data: Dict):
        persona = cls(data["persona_id"], data["name"], data.get("description", ""))
        persona.voice_samples = data.get("voice_samples", [])
        persona.text_samples = data.get("text_samples", [])
        persona.personality_traits = data.get("personality_traits", {})
        persona.memory = data.get("memory", [])
        persona.distilled_model_path = data.get("distilled_model_path")
        return persona

class PersonaManager:
    def __init__(self, storage_path: str = "./data/personas"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

    def create_persona(self, name: str, description: str = "") -> Persona:
        persona_id = name.lower().replace(" ", "_")
        persona = Persona(persona_id, name, description)
        self._save_persona(persona)
        return persona

    def load_persona(self, persona_id: str) -> Optional[Persona]:
        file_path = os.path.join(self.storage_path, f"{persona_id}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return Persona.from_dict(data)
        return None

    def _save_persona(self, persona: Persona):
        file_path = os.path.join(self.storage_path, f"{persona.persona_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(persona.to_dict(), f, ensure_ascii=False, indent=2)

    def list_personas(self) -> List[Persona]:
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

class ChatEngine:
    def __init__(self, model_provider: str = "ollama", model_name: str = "qwen2.5"):
        self.model_provider = model_provider
        self.model_name = model_name
        self.conversations: Dict[str, List[Dict]] = {}

    def generate_prompt(self, persona: Persona, message: str) -> str:
        traits_str = ", ".join([f"{k}: {v}" for k, v in persona.personality_traits.items()])
        prompt = f"""
你现在是{persona.name}，请用{persona.name}的身份和语气回答问题。

{persona.name}的描述：{persona.description}

{persona.name}的性格特点：{traits_str}

请用自然、亲切的方式回复，保持角色一致性。

用户说：{message}

你的回复：
"""
        return prompt.strip()

    def chat(self, persona: Persona, message: str, conversation_id: str = "default") -> str:
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []

        self.conversations[conversation_id].append({"role": "user", "content": message})

        prompt = self.generate_prompt(persona, message)

        response = self._call_model(prompt)

        self.conversations[conversation_id].append({"role": "assistant", "content": response})

        return response

    def _call_model(self, prompt: str) -> str:
        if self.model_provider == "ollama":
            return self._call_ollama(prompt)
        elif self.model_provider == "openai":
            return self._call_openai(prompt)
        else:
            return f"模型响应: {prompt[:50]}..."

    def _call_ollama(self, prompt: str) -> str:
        try:
            import ollama
            response = ollama.chat(model=self.model_name, messages=[{"role": "user", "content": prompt}])
            return response["message"]["content"]
        except ImportError:
            return "请安装 ollama 库: pip install ollama"
        except Exception as e:
            return f"Ollama调用失败: {str(e)}"

    def _call_openai(self, prompt: str) -> str:
        try:
            from openai import OpenAI
            client = OpenAI()
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except ImportError:
            return "请安装 openai 库: pip install openai"
        except Exception as e:
            return f"OpenAI调用失败: {str(e)}"

class ModelDistiller:
    def __init__(self, base_model: str = "qwen2.5:7b", target_model_size: str = "7b"):
        self.base_model = base_model
        self.target_model_size = target_model_size

    def extract_features(self, persona: Persona) -> Dict:
        features = {
            "text_style": self._analyze_text_style(persona),
            "speech_patterns": self._analyze_speech_patterns(persona),
            "personality_vector": list(persona.personality_traits.values())
        }
        return features

    def _analyze_text_style(self, persona: Persona) -> Dict:
        return {
            "avg_sentence_length": 15,
            "vocabulary_diversity": 0.8,
            "formality": 0.6,
            "emotional_tone": "warm"
        }

    def _analyze_speech_patterns(self, persona: Persona) -> Dict:
        return {
            "speaking_rate": "medium",
            "pitch_variation": "moderate",
            "accent": "neutral"
        }

    def distill(self, persona: Persona, output_path: str) -> str:
        features = self.extract_features(persona)
        
        distilled_model = {
            "persona_id": persona.persona_id,
            "base_model": self.base_model,
            "features": features,
            "fine_tune_config": {
                "learning_rate": 2e-5,
                "epochs": 3,
                "batch_size": 4
            }
        }

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(distilled_model, f, ensure_ascii=False, indent=2)

        persona.distilled_model_path = output_path
        return output_path

class AICompanion:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.persona_manager = PersonaManager(
            self.config.get("storage_path", "./data/personas")
        )
        self.chat_engine = ChatEngine(
            self.config.get("model_provider", "ollama"),
            self.config.get("model_name", "qwen2.5")
        )
        self.distiller = ModelDistiller(
            self.config.get("base_model", "qwen2.5:7b"),
            self.config.get("target_model_size", "7b")
        )

    def create_persona(self, name: str, description: str = "") -> Persona:
        return self.persona_manager.create_persona(name, description)

    def load_persona(self, persona_id: str) -> Optional[Persona]:
        return self.persona_manager.load_persona(persona_id)

    def list_personas(self) -> List[Persona]:
        return self.persona_manager.list_personas()

    def chat(self, persona_id: str, message: str, conversation_id: str = "default") -> str:
        persona = self.persona_manager.load_persona(persona_id)
        if not persona:
            return f"未找到人格档案: {persona_id}"
        return self.chat_engine.chat(persona, message, conversation_id)

    def distill_model(self, persona_id: str) -> str:
        persona = self.persona_manager.load_persona(persona_id)
        if not persona:
            return f"未找到人格档案: {persona_id}"

        output_path = f"./models/distilled/{persona_id}.json"
        result = self.distiller.distill(persona, output_path)
        self.persona_manager._save_persona(persona)
        return f"模型蒸馏完成: {result}"

    def add_memory(self, persona_id: str, memory: Dict):
        persona = self.persona_manager.load_persona(persona_id)
        if persona:
            persona.memory.append(memory)
            self.persona_manager._save_persona(persona)

    def get_memories(self, persona_id: str) -> List[Dict]:
        persona = self.persona_manager.load_persona(persona_id)
        return persona.memory if persona else []

if __name__ == "__main__":
    companion = AICompanion()
    
    grandma = companion.create_persona(
        name="奶奶",
        description="一位温柔善良的老奶奶，喜欢讲故事，关心家人"
    )
    
    grandma.add_personality_trait("温柔", 0.9)
    grandma.add_personality_trait("耐心", 0.85)
    grandma.add_personality_trait("慈祥", 0.95)
    companion.persona_manager._save_persona(grandma)
    
    response = companion.chat("奶奶", "奶奶，我今天工作好累啊")
    print(f"奶奶: {response}")
    
    result = companion.distill_model("奶奶")
    print(result)