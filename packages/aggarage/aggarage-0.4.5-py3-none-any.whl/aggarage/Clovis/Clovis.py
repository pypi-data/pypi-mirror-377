import math
import random
import re
import os
import pandas as pd
from collections import defaultdict, Counter

class Clovis:
    def __init__(self, model_file='Clovis.feather', max_n=7, output_length=100):
        self.model_name = 'Clovis'
        self.model_file = model_file
        self.max_n = max_n
        self.output_length = output_length
        self.models = self._load_or_train()

    @staticmethod
    def _mat_mul(A, B):
        result = []
        for i in range(len(A)):
            result.append([])
            for j in range(len(B[0])):
                result[i].append(sum(A[i][k] * B[k][j] for k in range(len(B))))
        return result

    @staticmethod
    def _softmax(x):
        if not x: return []
        exp_x = [math.exp(v - max(x)) for v in x]
        sum_exp_x = sum(exp_x)
        return [e / sum_exp_x for e in exp_x]

    def _self_attention(self, Q, K, V):
        scores = []
        if not Q or not Q[0]: return []
        for i in range(len(Q)):
            row = []
            for j in range(len(K)):
                score = sum(Q[i][idx] * K[j][idx] for idx in range(len(Q[i])))
                row.append(score)
            scores.append(row)
        attention_weights = [self._softmax(row) for row in scores]
        if not attention_weights or not V: return []
        output = []
        for i in range(len(V)):
            weighted_sum = [sum(attention_weights[i][k] * V[k][j] for k in range(len(V)))
                            for j in range(len(V[0]))]
            output.append(weighted_sum)
        return output

    def _multi_head_attention(self, Q, K, V, num_heads):
        if not Q or not Q[0]: return V
        d_model = len(Q[0])
        if num_heads == 0 or d_model % num_heads != 0: return V
        head_size = d_model // num_heads
        outputs = []
        for head in range(num_heads):
            q_head = [row[head * head_size:(head + 1) * head_size] for row in Q]
            k_head = [row[head * head_size:(head + 1) * head_size] for row in K]
            v_head = [row[head * head_size:(head + 1) * head_size] for row in V]
            attention_output = self._self_attention(q_head, k_head, v_head)
            outputs.extend(attention_output)
        return outputs

    @staticmethod
    def _positional_encoding(seq_len, d_model):
        encoding = []
        for pos in range(seq_len):
            row = []
            for i in range(d_model):
                term = pos / (10000 ** ((2 * (i // 2)) / d_model))
                row.append(math.sin(term) if i % 2 == 0 else math.cos(term))
            encoding.append(row)
        return encoding

    @staticmethod
    def _add_positional_encoding(embeddings, positional_encodings):
        return [[val + positional_encodings[i][j] for j, val in enumerate(row)]
                for i, row in enumerate(embeddings)]

    def _feed_forward_network(self, x):
        if not x or not x[0]: return []
        input_dim = len(x[0])
        hidden_dim = input_dim * 4
        W1 = [[random.uniform(-0.1, 0.1) for _ in range(hidden_dim)] for _ in range(input_dim)]
        b1 = [0] * hidden_dim
        W2 = [[random.uniform(-0.1, 0.1) for _ in range(input_dim)] for _ in range(hidden_dim)]
        b2 = [0] * input_dim
        hidden = [[max(0, val + b1[j]) for j, val in enumerate(row)] for row in self._mat_mul(x, W1)]
        output = [[val + b2[j] for j, val in enumerate(row)] for row in self._mat_mul(hidden, W2)]
        return output

    @staticmethod
    def _tokenize(text):
        return re.findall(r"\w+|[^\w\s]", text.lower())

    @staticmethod
    def _detokenize(tokens):
        # Join special tokens (like <|endoftext|>) without spaces, others with spaces
        out = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.startswith('<') and token.endswith('>'):
                # Join consecutive special tokens as one
                special = token
                while i + 1 < len(tokens) and tokens[i+1].startswith('<') and tokens[i+1].endswith('>'):
                    special += tokens[i+1]
                    i += 1
                out.append(special)
            else:
                out.append(token)
            i += 1
        text = ' '.join(out)
        text = text.replace('’', "'")
        text = re.sub(r" ?' ?(s|ve|re|ll|d|m|t)", r"'\1", text)
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        text = re.sub(r'<\s*\|\s*endoftext\s*\|\s*>', '<|endoftext|>', text)
        return text

    def _build_statistical_models(self, corpus_text):
        words = self._tokenize(corpus_text)
        models = defaultdict(lambda: defaultdict(Counter))
        models[1] = Counter(words)
        for n in range(2, self.max_n + 1):
            print(f"Building {n}-gram model...")
            for i in range(len(words) - n + 1):
                prefix = tuple(words[i: i + n - 1])
                suffix = words[i + n - 1]
                models[n][prefix][suffix] += 1
        return models
    
    def _predict_next_word_statistical(self, text):
        words = self._tokenize(text)
        if not words: return ''

        for n in range(self.max_n, 1, -1):
            if len(words) >= n - 1:
                prefix = tuple(words[-(n - 1):])
                if prefix in self.models.get(n, {}):
                    candidates = self.models[n][prefix]
                    population = list(candidates.keys())
                    weights = list(candidates.values())
                    return random.choices(population, weights=weights, k=1)[0]
        
        if self.models.get(1):
            unigram_candidates = self.models[1]
            population = list(unigram_candidates.keys())
            weights = list(unigram_candidates.values())
            return random.choices(population, weights=weights, k=1)[0]
        
        return ''

    def _predict_next_word_with_attention(self, text):
        tokens = self._tokenize(text)
        if not tokens: return ''
        
        d_model = 4
        num_heads = 2
        embeddings = [[random.random() for _ in range(d_model)] for _ in tokens]
        positional_encodings = self._positional_encoding(len(tokens), d_model)
        encoded_embeddings = self._add_positional_encoding(embeddings, positional_encodings)
        
        attention_output = self._multi_head_attention(encoded_embeddings, encoded_embeddings, encoded_embeddings, num_heads)
        ff_output = self._feed_forward_network(attention_output)

        return self._predict_next_word_statistical(text)

    def save_model(self):
        print(f"\nSaving model to {self.model_file}...")
        model_data = []
        if 1 in self.models:
            for word, count in self.models[1].items():
                model_data.append({'n': 1, 'prefix': '_UNIGRAM_', 'suffix': word, 'count': count})
        
        for n, prefixes in self.models.items():
            if n > 1:
                for prefix, counter in prefixes.items():
                    for suffix, count in counter.items():
                        model_data.append({
                            'n': n, 'prefix': ' '.join(prefix), 'suffix': suffix, 'count': count
                        })
        df = pd.DataFrame(model_data)
        df.to_feather(self.model_file)
        print("Model saved successfully.")

    def load_model(self):
        print(f"Loading model from {self.model_file}...")
        df = pd.read_feather(self.model_file)
        models = defaultdict(lambda: defaultdict(Counter))
        
        unigram_df = df[df['n'] == 1]
        models[1] = Counter(dict(zip(unigram_df['suffix'], unigram_df['count'])))
        
        ngram_df = df[df['n'] > 1]
        for _, row in ngram_df.iterrows():
            n, prefix_str, suffix, count = row['n'], row['prefix'], row['suffix'], row['count']
            prefix = tuple(prefix_str.split())
            models[n][prefix][suffix] += count
        print("Model loaded successfully.")
        return models

    def train(self, corpus_text):
        print(f'\nTraining for {self.model_name} has begun.')
        cleaned_corpus = re.sub(r'[\r\n]+', ' ', corpus_text.strip())
        self.models = self._build_statistical_models(cleaned_corpus)
        self.save_model()
        print('\nTraining complete.')

    def _load_or_train(self):
        if os.path.exists(self.model_file):
            return self.load_model()
        else:
            from .corpus import corpus
            self.train(corpus)
            return self.models

    def generate_response(self, input_text):
        context = input_text.lower()
        if not self._tokenize(context): return "Please say something."
        
        generated_tokens = []
        for _ in range(self.output_length):
            prediction = self._predict_next_word_with_attention(context)
            if not prediction: break
            generated_tokens.append(prediction)
            context += ' ' + prediction
            context = ' '.join(context.split())

        return self._detokenize(generated_tokens)


if __name__ == "__main__":
    try:
        from .corpus import corpus
        model = Clovis()
        while True:
            try:
                input_text = input('You: ').strip()
                if input_text.lower() in ['exit', 'quit', 'goodbye']:
                    print(f'{model.model_name}: Goodbye!')
                    break
                predicted_sentence = model.generate_response(input_text)
                print(f'{model.model_name}: {predicted_sentence}')
            except (KeyboardInterrupt, EOFError):
                print(f'\n{model.model_name}: Goodbye!')
                break
    except ImportError:
        try:
            from corpus import corpus
            model = Clovis()
            while True:
                try:
                    input_text = input('You: ').strip()
                    if input_text.lower() in ['exit', 'quit', 'goodbye']:
                        print(f'{model.model_name}: Goodbye!')
                        break
                    predicted_sentence = model.generate_response(input_text)
                    print(f'{model.model_name}: {predicted_sentence}')
                except (KeyboardInterrupt, EOFError):
                    print(f'\n{model.model_name}: Goodbye!')
                    break
        except ImportError:
            print("Error: `corpus.py` not found.")
            print("Please ensure you have a file named `corpus.py` with a `corpus` variable containing your training text.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")