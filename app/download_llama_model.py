from huggingface_hub import login, hf_hub_download

login()

path = hf_hub_download(
    repo_id="TheBloke/Llama-2-7B-Chat-GGUF",
    filename="llama-2-7b-chat.Q4_K_M.gguf",
    local_dir="./models",
    local_dir_use_symlinks=False
)

print("✅ Download completed. File saved at:", path)
