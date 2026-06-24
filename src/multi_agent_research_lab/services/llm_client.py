"""LLM client implementation loading Hugging Face model directly from disk."""

import os
from dataclasses import dataclass
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Loads a Hugging Face model from D drive and generates responses offline."""

    """Loads a Hugging Face model and generates responses.
    
    Implemented as a Singleton to prevent loading the model multiple times 
    in GPU memory.
    """
    _instance = None
    def __new__(cls, *args, **kwargs):
        # Mẫu thiết kế Singleton: Trả về thực thể duy nhất đã tạo
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self) -> None:
        # Nếu đã khởi tạo và nạp model rồi thì bỏ qua không nạp lại
        if self._initialized:
            return
        # CẤU HÌNH: ID mô hình trên Hugging Face
        self.model_path = "Qwen/Qwen2.5-7B-Instruct" 
        
        # Load Tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        
        # Chọn thiết bị chạy
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load Model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
        )
        
        # Di chuyển model lên GPU/CPU
        self.model = self.model.to(self.device)
        
        # Đánh dấu đã khởi tạo thành công
        self._initialized = True

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Run inference directly in Python using PyTorch."""
        
        # 1. Tạo cấu trúc tin nhắn Chat Template
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 2. Định dạng prompt theo chuẩn chat của model
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        input_tokens = inputs["input_ids"].shape[1]
        
        # 3. Thực hiện sinh câu trả lời (Inference)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=1024,      # Giới hạn độ dài câu trả lời tối đa
                temperature=0.2,           # Độ sáng tạo thấp để giữ tính chính xác học thuật
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
        # 4. Giải mã kết quả (bỏ đi phần prompt câu hỏi ban đầu)
        generated_ids = outputs[0][inputs["input_ids"].shape[1]:]
        content = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
        output_tokens = len(generated_ids)
        
        return LLMResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=0.0 # Chạy local offline hoàn toàn miễn phí
        )
