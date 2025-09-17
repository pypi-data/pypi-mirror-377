model_name = "RAShaw/llama-3.2-3b-instruct"
from transformers import AutoModelForCausalLM, AutoTokenizer

print(f"Loading {model_name}...")
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name, device_map="auto", torch_dtype="auto", trust_remote_code=True
)
inputs = tokenizer("Hello, my dog is cute", return_tensors="pt").to("cuda")
generate_ids = model.generate(**inputs, max_new_tokens=50)
print(
    tokenizer.batch_decode(
        generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )[0]
)
