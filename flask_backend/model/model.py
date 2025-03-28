from transformers import BertTokenizer, BertForSequenceClassification
import torch

def load_model():
    model_path = "ZheZHEZHE020106/zt-harmful_language_detecting"
    tokenizer = BertTokenizer.from_pretrained(model_path)
    model = BertForSequenceClassification.from_pretrained(model_path)
    return tokenizer, model

def predict(tokenizer, model, input, device):
    inputs = tokenizer(input, return_tensors="pt", padding=True, truncation=True, max_length=256)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class = torch.argmax(logits, dim=1).item()

    if predicted_class == 1:
        print("检测为恶意评论 / 非法文本")
    else:
        print("检测为正常文本")

def main():
    tokenizer, model = load_model()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    input = """
        Hi, we are group 5
    """

    predict(tokenizer, model, input, device)

if __name__ == '__main__':
    main()