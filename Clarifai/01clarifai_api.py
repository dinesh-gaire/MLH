from clarifai.client.model import Model

prompt = "What's the future of AI?"

model_url="https://clarifai.com/deepseek-ai/deepseek-chat/models/DeepSeek-R1-0528-Qwen3-8B"
model_prediction = Model(url=model_url, pat="your_pat_key").predict_by_bytes(prompt.encode())

print(model_prediction.outputs[0].data.text.raw)