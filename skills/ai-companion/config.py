from typing import Dict, Any

DEFAULT_CONFIG: Dict[str, Any] = {
    "model": {
        "provider": "ollama",
        "name": "qwen2.5",
        "base_model": "qwen2.5:7b",
        "api_key": None,
        "max_tokens": 1024,
        "temperature": 0.7,
        "top_p": 0.9
    },
    "storage": {
        "personas_path": "./data/personas",
        "models_path": "./models",
        "datasets_path": "./data/datasets",
        "memory_path": "./data/memory"
    },
    "distillation": {
        "method": "lora",
        "epochs": 3,
        "batch_size": 4,
        "learning_rate": 2e-4,
        "target_size": "7b"
    },
    "privacy": {
        "local_only": True,
        "encryption_enabled": True,
        "auto_delete_conversations": False,
        "data_retention_days": 30
    },
    "ui": {
        "theme": "light",
        "language": "zh",
        "show_emotions": True,
        "typing_effect": True
    }
}

class ConfigManager:
    def __init__(self, config_path: str = "./config/config.yaml"):
        self.config_path = config_path
        self.config = DEFAULT_CONFIG.copy()

    def load(self) -> Dict[str, Any]:
        try:
            import yaml
            with open(self.config_path, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f)
                if user_config:
                    self.config = self._deep_merge(DEFAULT_CONFIG, user_config)
        except FileNotFoundError:
            pass
        except ImportError:
            pass
        except Exception as e:
            print(f"配置加载失败: {e}")
        
        return self.config

    def save(self, config: Dict[str, Any]):
        import os
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        try:
            import yaml
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        except ImportError:
            import json
            with open(self.config_path.replace(".yaml", ".json"), "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        result = base.copy()
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        keys = key.split(".")
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

if __name__ == "__main__":
    config_manager = ConfigManager()
    config = config_manager.load()
    print("配置加载成功")
    print("模型提供者:", config.get("model.provider"))
    print("人格存储路径:", config.get("storage.personas_path"))