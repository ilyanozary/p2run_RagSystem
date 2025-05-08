from huggingface_hub import hf_hub_download
import os

repo_id = "TheBloke/Llama-2-7B-Chat-GGUF"  
filename = "llama-2-7b-chat.Q4_K_M.gguf"   
destination_folder = "models"              

os.makedirs(destination_folder, exist_ok=True)
model_path = hf_hub_download(repo_id=repo_id, filename=filename, local_dir=destination_folder)

print(f"✅ download model {model_path}")
