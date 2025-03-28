# import torch
# from transformers import BertTokenizer, BertForSequenceClassification


# def load_model():
#     model_path = "ZheZHEZHE020106/zt-harmful_language_detecting"
#     tokenizer = BertTokenizer.from_pretrained(model_path)
#     model = BertForSequenceClassification.from_pretrained(model_path)
#     return tokenizer, model

# def predict(tokenizer, model, input, device):
#     inputs = tokenizer(input, return_tensors="pt", padding=True, truncation=True, max_length=256)
#     inputs = {k: v.to(device) for k, v in inputs.items()}

#     with torch.no_grad():
#         outputs = model(**inputs)
#         logits = outputs.logits
#         predicted_class = torch.argmax(logits, dim=1).item()

#     return predicted_class # 1 for harmful language, 0 for normal

# def main():
#     tokenizer, model = load_model()
#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#     model.to(device)

#     input = """
#         Hi, we are group 5
#     """

#     predict(tokenizer, model, input, device)

# if __name__ == '__main__':
#     main()


from transformers import BertForSequenceClassification, BertTokenizer
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

#load model and parameters
model = BertForSequenceClassification.from_pretrained("ZheZHEZHE020106/zt-harmful_language_detecting")
tokenizer = BertTokenizer.from_pretrained("ZheZHEZHE020106/zt-harmful_language_detecting")

model.to(device)
model.eval()

def predict(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=256)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        logits = model(**inputs).logits
        pred = torch.argmax(logits, dim=1).item()
    return pred  # 1 = toxic, 0 = normal