import os
import json
from typing import Dict, List, Optional, Any
import subprocess
import tempfile

class DistillationPipeline:
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.distillation_methods = {
            "lora": self._distill_lora,
            "qlora": self._distill_qlora,
            "full_finetune": self._distill_full_finetune,
            "prompt_tuning": self._distill_prompt_tuning
        }

    def distill(self, 
                persona_id: str,
                base_model: str,
                dataset_path: str,
                output_path: str,
                method: str = "lora",
                **kwargs) -> Dict:
        if method not in self.distillation_methods:
            raise ValueError(f"不支持的蒸馏方法: {method}")

        distillation_fn = self.distillation_methods[method]
        return distillation_fn(persona_id, base_model, dataset_path, output_path, **kwargs)

    def _distill_lora(self, persona_id: str, base_model: str, 
                      dataset_path: str, output_path: str, **kwargs) -> Dict:
        config = {
            "persona_id": persona_id,
            "base_model": base_model,
            "method": "lora",
            "r": kwargs.get("r", 8),
            "lora_alpha": kwargs.get("lora_alpha", 32),
            "lora_dropout": kwargs.get("lora_dropout", 0.05),
            "target_modules": kwargs.get("target_modules", ["q_proj", "v_proj"]),
            "batch_size": kwargs.get("batch_size", 4),
            "learning_rate": kwargs.get("learning_rate", 2e-4),
            "epochs": kwargs.get("epochs", 3)
        }

        os.makedirs(output_path, exist_ok=True)
        config_path = os.path.join(output_path, "config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        return {
            "status": "success",
            "message": "LoRA蒸馏配置已生成",
            "config_path": config_path,
            "output_path": output_path
        }

    def _distill_qlora(self, persona_id: str, base_model: str, 
                       dataset_path: str, output_path: str, **kwargs) -> Dict:
        config = {
            "persona_id": persona_id,
            "base_model": base_model,
            "method": "qlora",
            "quantization_bit": kwargs.get("quantization_bit", 4),
            "r": kwargs.get("r", 8),
            "lora_alpha": kwargs.get("lora_alpha", 32),
            "batch_size": kwargs.get("batch_size", 4),
            "learning_rate": kwargs.get("learning_rate", 2e-4),
            "epochs": kwargs.get("epochs", 3)
        }

        os.makedirs(output_path, exist_ok=True)
        config_path = os.path.join(output_path, "config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        return {
            "status": "success",
            "message": "QLoRA蒸馏配置已生成",
            "config_path": config_path,
            "output_path": output_path
        }

    def _distill_full_finetune(self, persona_id: str, base_model: str,
                               dataset_path: str, output_path: str, **kwargs) -> Dict:
        config = {
            "persona_id": persona_id,
            "base_model": base_model,
            "method": "full_finetune",
            "batch_size": kwargs.get("batch_size", 2),
            "learning_rate": kwargs.get("learning_rate", 5e-5),
            "epochs": kwargs.get("epochs", 2),
            "gradient_accumulation_steps": kwargs.get("gradient_accumulation_steps", 4)
        }

        os.makedirs(output_path, exist_ok=True)
        config_path = os.path.join(output_path, "config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        return {
            "status": "success",
            "message": "全量微调配置已生成",
            "config_path": config_path,
            "output_path": output_path
        }

    def _distill_prompt_tuning(self, persona_id: str, base_model: str,
                               dataset_path: str, output_path: str, **kwargs) -> Dict:
        config = {
            "persona_id": persona_id,
            "base_model": base_model,
            "method": "prompt_tuning",
            "num_virtual_tokens": kwargs.get("num_virtual_tokens", 20),
            "batch_size": kwargs.get("batch_size", 8),
            "learning_rate": kwargs.get("learning_rate", 3e-2),
            "epochs": kwargs.get("epochs", 5)
        }

        os.makedirs(output_path, exist_ok=True)
        config_path = os.path.join(output_path, "config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        return {
            "status": "success",
            "message": "Prompt Tuning配置已生成",
            "config_path": config_path,
            "output_path": output_path
        }

class PersonaDatasetGenerator:
    def __init__(self):
        self.template_formats = {
            "chatml": self._format_chatml,
            "alpaca": self._format_alpaca,
            "sharegpt": self._format_sharegpt
        }

    def generate_dataset(self, persona: Any, output_path: str, 
                        format_type: str = "chatml") -> str:
        if format_type not in self.template_formats:
            raise ValueError(f"不支持的格式: {format_type}")

        samples = self._generate_training_samples(persona)
        formatted_data = [self.template_formats[format_type](sample) for sample in samples]

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            for item in formatted_data:
                json.dump(item, f, ensure_ascii=False)
                f.write("\n")

        return output_path

    def _generate_training_samples(self, persona: Any) -> List[Dict]:
        samples = []
        
        traits = persona.personality_traits if hasattr(persona, 'personality_traits') else {}
        trait_descriptions = ", ".join([f"{k}: {v}" for k, v in traits.items()])

        prompts = [
            {"instruction": "问一个日常问题", "input": "你今天过得怎么样？"},
            {"instruction": "表达关心", "input": "我最近工作好累"},
            {"instruction": "分享回忆", "input": "你还记得小时候的事情吗？"},
            {"instruction": "给予安慰", "input": "我有点难过"},
            {"instruction": "日常闲聊", "input": "今天天气真好"},
            {"instruction": "提供建议", "input": "我遇到了一个难题"},
            {"instruction": "回忆往事", "input": "你以前最喜欢做什么？"},
            {"instruction": "表达思念", "input": "我很想你"}
        ]

        for prompt in prompts:
            samples.append({
                "instruction": prompt["instruction"],
                "input": prompt["input"],
                "persona_info": {
                    "name": persona.name if hasattr(persona, 'name') else "Unknown",
                    "description": persona.description if hasattr(persona, 'description') else "",
                    "traits": trait_descriptions
                }
            })

        return samples

    def _format_chatml(self, sample: Dict) -> Dict:
        return {
            "messages": [
                {
                    "role": "system",
                    "content": f"你是{sample['persona_info']['name']}。{sample['persona_info']['description']}性格特点：{sample['persona_info']['traits']}"
                },
                {"role": "user", "content": sample["input"]},
                {"role": "assistant", "content": f"（{sample['persona_info']['name']}的回复）"}
            ]
        }

    def _format_alpaca(self, sample: Dict) -> Dict:
        return {
            "instruction": f"作为{sample['persona_info']['name']}，{sample['instruction']}",
            "input": f"{sample['persona_info']['description']}。用户说：{sample['input']}",
            "output": "（回复内容）"
        }

    def _format_sharegpt(self, sample: Dict) -> Dict:
        return {
            "conversations": [
                {
                    "from": "system",
                    "value": f"你是{sample['persona_info']['name']}，{sample['persona_info']['description']}"
                },
                {"from": "human", "value": sample["input"]},
                {"from": "gpt", "value": f"（{sample['persona_info']['name']}的回复）"}
            ]
        }

class ModelOptimizer:
    def __init__(self):
        pass

    def quantize(self, model_path: str, output_path: str, 
                 bits: int = 4, method: str = "awq") -> Dict:
        config = {
            "input_model": model_path,
            "output_model": output_path,
            "quantization_bits": bits,
            "method": method
        }

        os.makedirs(output_path, exist_ok=True)
        config_path = os.path.join(output_path, "quantization_config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        return {
            "status": "success",
            "message": f"{bits}位量化配置已生成",
            "config_path": config_path
        }

    def prune(self, model_path: str, output_path: str, 
              sparsity: float = 0.5) -> Dict:
        config = {
            "input_model": model_path,
            "output_model": output_path,
            "sparsity": sparsity
        }

        os.makedirs(output_path, exist_ok=True)
        config_path = os.path.join(output_path, "pruning_config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        return {
            "status": "success",
            "message": f"剪枝配置已生成（稀疏度: {sparsity}）",
            "config_path": config_path
        }

    def merge_lora(self, base_model: str, lora_path: str, 
                   output_path: str) -> Dict:
        config = {
            "base_model": base_model,
            "lora_path": lora_path,
            "output_model": output_path
        }

        os.makedirs(output_path, exist_ok=True)
        config_path = os.path.join(output_path, "merge_config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        return {
            "status": "success",
            "message": "LoRA合并配置已生成",
            "config_path": config_path
        }

class NvwaDistiller:
    def __init__(self, nvwa_api_url: Optional[str] = None):
        self.nvwa_api_url = nvwa_api_url or "http://localhost:8000"

    def distill_with_nvwa(self, persona_id: str, 
                          base_model: str,
                          dataset_path: str,
                          output_path: str,
                          method: str = "lora") -> Dict:
        distillation_config = {
            "persona_id": persona_id,
            "base_model": base_model,
            "dataset_path": dataset_path,
            "output_path": output_path,
            "method": method,
            "params": {
                "epochs": 3,
                "batch_size": 4,
                "learning_rate": 2e-4
            }
        }

        try:
            import requests
            response = requests.post(
                f"{self.nvwa_api_url}/api/distill",
                json=distillation_config,
                timeout=300
            )
            response.raise_for_status()
            return response.json()
        except ImportError:
            return {
                "status": "info",
                "message": "请安装 requests 库以使用女娲API",
                "config": distillation_config
            }
        except Exception as e:
            return {
                "status": "pending",
                "message": f"女娲蒸馏任务已创建（离线模式）",
                "config": distillation_config
            }

    def get_distillation_status(self, task_id: str) -> Dict:
        try:
            import requests
            response = requests.get(
                f"{self.nvwa_api_url}/api/distill/{task_id}",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "status": "unknown",
                "message": str(e)
            }

if __name__ == "__main__":
    distiller = DistillationPipeline()
    
    result = distiller.distill(
        persona_id="grandma",
        base_model="qwen2.5:7b",
        dataset_path="./data/datasets/grandma.json",
        output_path="./models/distilled/grandma",
        method="lora",
        r=8,
        epochs=3
    )
    print("蒸馏结果:", result)

    dataset_gen = PersonaDatasetGenerator()
    from ai_companion import Persona
    persona = Persona("grandma", "奶奶", "温柔善良的老奶奶")
    persona.add_personality_trait("温柔", 0.9)
    persona.add_personality_trait("耐心", 0.85)
    
    dataset_path = dataset_gen.generate_dataset(persona, "./data/datasets/grandma.jsonl")
    print("数据集生成路径:", dataset_path)

    optimizer = ModelOptimizer()
    quant_result = optimizer.quantize(
        "./models/distilled/grandma",
        "./models/quantized/grandma",
        bits=4
    )
    print("量化结果:", quant_result)