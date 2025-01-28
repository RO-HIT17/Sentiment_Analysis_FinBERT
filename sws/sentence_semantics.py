from transformers import AutoTokenizer, AutoModel
import torch


tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/msmarco-distilbert-cos-v5')
model = AutoModel.from_pretrained('sentence-transformers/msmarco-distilbert-cos-v5')


def mean_pooling(model_output, attention_mask):
    """
    Mean Pooling - taking average of all tokens
    :param model_output:
    :param attention_mask:
    :return:
    """
    token_embeddings = model_output.last_hidden_state   # First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


def encode(texts: [str, list]) -> torch.Tensor:
    """
    Encodes text / standardized terms to extract embeddings
    :param texts: a string or a list of strings that represent query or standardized terms
    :return: a tensor that contains normalized embeddings
    """
    # Tokenize sentences
    encoded_input = tokenizer(texts, padding=True, truncation=True, return_tensors='pt')

    # Compute token embeddings
    with torch.no_grad():
        model_output = model(**encoded_input, return_dict=True)

    # Perform pooling
    embeddings = mean_pooling(model_output, encoded_input['attention_mask'])

    # Normalize embeddings
    embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)

    return embeddings


def compute_similarity(query: str, standard_terms: list, standard_terms_embeddings: torch.Tensor) -> list:
    """
    Computes similarity scores of a string query against defined standardized terms
    :param query: a string that represents certain part of text paragraph
    :param standard_terms: a list of standardized phrases
    :param standard_terms_embeddings: a list of standardized phrases embeddings
    :return: a sorted list that contains standardized phrases and similarity scores sorted in descending order
    """
    query_embeddings = encode(query)

    # Compute cosine similarity between query and standard terms embeddings
    scores = torch.nn.functional.cosine_similarity(query_embeddings, standard_terms_embeddings).tolist()

    # Combine standard terms and scores
    standard_terms_score_pairs = tuple(zip(standard_terms, scores))

    # Sort by descending order
    standard_terms_pairs = sorted(standard_terms_score_pairs, key=lambda x: x[1], reverse=True)

    return standard_terms_pairs


def main():
    pass


if __name__ == '__main__':
    main()


