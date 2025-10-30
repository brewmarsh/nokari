import torch
from transformers import AutoModel, AutoTokenizer

# Load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(
    "sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")


def generate_embedding(text):
    """
    Generates a sentence embedding for the given text using a pre-trained
    transformer model.

    Args:
        text (str): The input text to embed.

    Returns:
        list: A list of floats representing the embedding.
    """
    inputs = tokenizer(text, return_tensors="pt",
                       truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)

    # Mean pooling
    embeddings = outputs.last_hidden_state
    mask = inputs["attention_mask"].unsqueeze(
        -1).expand(embeddings.size()).float()
    masked_embeddings = embeddings * mask
    summed = torch.sum(masked_embeddings, 1)
    counted = torch.clamp(mask.sum(1), min=1e-9)
    mean_pooled = summed / counted

    # Normalize
    mean_pooled = torch.nn.functional.normalize(mean_pooled, p=2, dim=1)
    return mean_pooled.tolist()[0]
