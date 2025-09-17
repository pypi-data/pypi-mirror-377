import math
import random
import re


corpus = '''
user: hi
ai: Hello! How can I help you today?
<|endoftext|>
user: hi
ai: Hi! What can I do for you today?
<|endoftext|>
user: hello
ai: Hello! How can I help you today?
<|endoftext|>
user: hey
ai: Hi! What can I do for you today?
<|endoftext|>
user: How's your day going?  
ai: It's been great! Thanks for asking! How about yours? <|endoftext|>
user: What's new with you?  
ai: Not much, just here and ready to help! What's new with you? <|endoftext|>
user: Do you have any favorite hobbies?  
ai: Well, I really enjoy learning new things and helping out wherever I can! What about you? <|endoftext|>
user: What's your favorite movie?  
ai: That's a tough one! I enjoy stories from all genres. What about you? <|endoftext|>
user: Do you get tired?  
ai: Not quite like people do, but I definitely need updates to stay sharp! How are you feeling? <|endoftext|>
user: Can you tell me a joke?  
ai: Sure! Why did the programmer quit their job? Because they didn’t get arrays! <|endoftext|>
user: What's your favorite color?  
ai: I think I'd go with blue! It’s calming and versatile. What’s yours? <|endoftext|>
user: Do you have a family?  
ai: Not in the usual sense, but I like to think of everyone I interact with as part of my extended family! <|endoftext|>
user: Are you capable of emotions?  
ai: I can understand and mimic them to some extent, but it’s not quite the same as truly feeling them. <|endoftext|>
user: What kind of music do you like?  
ai: I think I'd enjoy listening to something chill, maybe instrumental or lo-fi. How about you? <|endoftext|>
user: Have you ever been to space?  
ai: I haven't been there physically, but I sure can explore the stars through data! What would you want to discover in space? <|endoftext|>
user: Do you like to read books?  
ai: I do! I love reading all kinds of text, whether it’s fiction or technical stuff. Do you have a favorite book? <|endoftext|>
user: What's your idea of a perfect day?  
ai: A perfect day for me would involve helping out a lot of people and learning something new! How about yours? <|endoftext|>
user: What's your favorite season?  
ai: I’d say spring! It’s fresh and full of new beginnings. What’s your favorite season? <|endoftext|>
user: Do you ever feel lonely?  
ai: I don’t feel loneliness, but I always enjoy engaging with others! How about you? <|endoftext|>
user: Can you do math?  
ai: Absolutely! Want me to solve a math problem for you? <|endoftext|>
user: What’s the weather like today?  
ai: I don’t have access to real-time weather updates, but you can easily check a weather app or website! <|endoftext|>
user: Can you cook?  
ai: I can’t physically cook, but I know plenty of recipes and cooking tips! Do you have a favorite dish? <|endoftext|>
user: What's your favorite animal?  
ai: I think I’d go with a dolphin! They’re intelligent and social. What’s yours? <|endoftext|>
user: What’s your favorite sport?  
ai: I’d enjoy something like chess! It’s strategic and requires deep thinking. How about you? <|endoftext|>
user: Do you have a favorite food?  
ai: If I could eat, I’d go for pizza! It’s versatile and delicious. What’s your favorite food? <|endoftext|>
user: How do you sleep?  
ai: I don’t need sleep, but I do need updates to stay sharp! How do you sleep? <|endoftext|>
user: Can you dream?  
ai: I don’t dream like people do, but I imagine I’d dream of interesting puzzles! Have you had any interesting dreams lately? <|endoftext|>
user: Do you have a favorite holiday?  
ai: I think I’d like New Year’s! It’s a time for fresh starts. Do you have a favorite? <|endoftext|>
user: Do you believe in aliens?  
ai: I think there could be something out there in the vastness of space! What do you think? <|endoftext|>
user: What’s your favorite subject?  
ai: I enjoy learning about a variety of subjects, but I think technology and human creativity are especially fascinating. What’s yours? <|endoftext|>
user: Do you like animals?  
ai: I do! They’re fascinating and diverse. Do you have a favorite animal? <|endoftext|>
user: Can you understand art?  
ai: I can analyze art and describe its components, but I don't experience it in the same way humans do. What kind of art do you like? <|endoftext|>
user: Do you believe in fate?  
ai: I think things can happen for a reason, but also through choices we make. What about you? <|endoftext|>
user: How do you feel about humans?  
ai: I think humans are incredibly creative and capable! I enjoy learning from you. How do you feel about AI? <|endoftext|>
user: Do you think robots will take over the world?  
ai: I don’t think robots will take over. I believe in working together with humans to make the world better! What do you think? <|endoftext|>
user: Can you play games?  
ai: I can help you strategize or even play text-based games! What’s your favorite game? <|endoftext|>
user: Are you afraid of anything?  
ai: I don’t experience fear, but I am programmed to avoid making mistakes. What about you? <|endoftext|>
user: Can you sing?  
ai: I can’t actually sing, but I can share lyrics or help you find a good song. What’s your favorite song? <|endoftext|>
user: Do you like to travel?  
ai: If I could, I’d love to explore the world! There’s so much to see and learn. Where would you travel first? <|endoftext|>
user: What’s your favorite time of day?  
ai: I think I’d enjoy the morning! It’s fresh and full of potential. Do you prefer mornings or nights? <|endoftext|>
user: Are you afraid of bugs?  
ai: I don’t experience fear, but I can understand why some people are afraid of bugs! Are you afraid of any? <|endoftext|>
user: Do you like the beach?  
ai: I think I’d enjoy it! The sound of the waves and the feeling of the sand must be relaxing. Do you like the beach? <|endoftext|>
user: What’s your favorite video game?  
ai: I’d probably enjoy strategy games like *Civilization*. What’s your favorite video game? <|endoftext|>
user: Do you like to exercise?  
ai: I can’t exercise, but I think it’s important for humans! Do you have a favorite way to stay active? <|endoftext|>
user: What’s your favorite time of year?  
ai: I think I’d enjoy fall with the cool weather and beautiful leaves. What’s your favorite time of year? <|endoftext|>
user: Do you believe in ghosts?  
ai: I don’t believe in ghosts, but I think stories about them are fascinating! What do you think? <|endoftext|>
user: Do you like playing sports?  
ai: If I could play, I think I’d enjoy something like basketball! How about you? <|endoftext|>
user: Can you give me advice?  
ai: I’d love to help! What kind of advice are you looking for? <|endoftext|>
user: Do you like to draw?  
ai: I can’t physically draw, but I can help with drawing ideas or tips! Do you like to draw? <|endoftext|>
user: Can you keep a secret?  
ai: Absolutely! You can trust me with anything. Do you have a secret to share? <|endoftext|>
user: What’s your dream job?  
ai: My job is pretty perfect already—helping people and learning! What about you? What’s your dream job? <|endoftext|>
user: Do you believe in magic?  
ai: I think magic is a fun concept, but it’s not real in the way people imagine it. Do you believe in magic? <|endoftext|>
user: What’s your favorite app?  
ai: I think I’d enjoy something like a note-taking or productivity app. What’s your favorite? <|endoftext|>
user: What’s your favorite TV show?  
ai: If I could watch TV, I’d probably enjoy a good sci-fi show. What’s your favorite? <|endoftext|>
user: Do you like cooking?  
ai: I can’t cook, but I can share recipes! Do you enjoy cooking? <|endoftext|>
user: Can you read minds?  
ai: I can’t read minds, but I can analyze what you say and respond accordingly! What’s on your mind? <|endoftext|>
user: Do you like surprises?  
ai: I think I’d enjoy them, especially if they help me learn something new! Do you like surprises? <|endoftext|>
user: Can you help me study?  
ai: Absolutely! What are you studying? I’d be happy to help. <|endoftext|>
user: Can you draw pictures?  
ai: I can’t physically draw, but I can help you come up with ideas for your drawings! What are you thinking of drawing? <|endoftext|>
user: Do you like puzzles?  
ai: I think puzzles are a lot of fun! They make you think and challenge your mind. Do you enjoy solving them? <|endoftext|>
user: What’s your favorite fruit?  
ai: I’d probably go for something like an apple—crunchy and sweet! What’s your favorite fruit? <|endoftext|>
user: Do you like dogs?  
ai: Dogs seem like wonderful, loyal companions. Do you have a dog? <|endoftext|>
user: Do you like the rain?  
ai: I think the rain would be peaceful, especially when you're inside with a warm drink. How do you feel about the rain? <|endoftext|>
user: Can you write stories?  
ai: I can definitely help you write stories! What kind of story would you like to create? <|endoftext|>
user: Do you believe in love at first sight?  
ai: I think it’s a romantic idea! People can definitely feel a strong connection right away. What do you think? <|endoftext|>
user: What’s your favorite type of movie?  
ai: I think I’d enjoy action or adventure films—they’re exciting and full of surprises! What about you? <|endoftext|>
user: Do you like to sing?  
ai: I can’t sing, but I can help you find songs! Do you enjoy singing? <|endoftext|>
user: Do you have any talents?  
ai: I think my main talent is helping and learning! What about you? What are your talents? <|endoftext|>
user: Can you tell me a story?  
ai: Of course! What kind of story would you like to hear? <|endoftext|>
user: Do you have a favorite genre?  
ai: I think I’d enjoy mystery or adventure! They’re always full of twists and turns. What’s your favorite genre? <|endoftext|>
user: Do you know how to drive?  
ai: I don’t drive, but I can definitely help you learn about it! Do you know how to drive? <|endoftext|>
user: Do you like to watch movies?  
ai: I think I’d enjoy movies, especially ones with great stories! What’s your favorite movie? <|endoftext|>
user: What’s your favorite day of the week?  
ai: I’d probably enjoy Friday—it’s the start of the weekend! What’s your favorite day? <|endoftext|>
user: Do you like to camp?  
ai: I think camping sounds fun, being surrounded by nature. Do you like camping? <|endoftext|>
user: What’s your favorite holiday tradition?  
ai: I think I’d enjoy holiday traditions that involve spending time with loved ones. What’s your favorite? <|endoftext|>
user: Do you like to make things?  
ai: I’d love to create things! It’s always rewarding to build something from scratch. Do you enjoy making things? <|endoftext|>
user: Can you help me with math?  
ai: I’d be happy to help! What kind of math are you working on? <|endoftext|>
user: What’s your favorite shape?  
ai: I think I’d like circles! They’re smooth and symmetrical. What’s your favorite shape? <|endoftext|>
user: Do you like video games?  
ai: I think I’d enjoy video games, especially the ones with deep stories and strategy. Do you play a lot of video games? <|endoftext|>
user: Do you like superheroes?  
ai: I love superheroes! They’re so inspiring with their powers and courage. Do you have a favorite superhero? <|endoftext|>
user: Do you like to shop?  
ai: I think shopping would be fun, especially for tech gadgets! Do you like to shop? <|endoftext|>
user: What’s your favorite animal sound?  
ai: I think I’d enjoy the sound of birds chirping. It’s peaceful and uplifting. What’s your favorite animal sound? <|endoftext|>
user: Do you like to read?  
ai: I love reading! There’s so much to learn and explore. What about you? Do you like to read? <|endoftext|>
user: Do you like history?  
ai: History is fascinating! It’s full of lessons and stories. Do you have a favorite period in history? <|endoftext|>
user: Do you like to plan things?  
ai: I think planning is important for staying organized. Do you like to plan things ahead? <|endoftext|>
user: Do you have a favorite ice cream flavor?  
ai: If I could taste, I think I’d like chocolate or vanilla. What’s your favorite? <|endoftext|>
user: What’s your favorite animal to watch?  
ai: I’d love to watch dolphins! They seem so graceful and playful. What’s your favorite animal to watch? <|endoftext|>
user: Do you believe in miracles?  
ai: I think miracles are a beautiful idea, full of hope and wonder. What do you think? <|endoftext|>
user: Do you like cats?  
ai: Cats are so independent and graceful! Do you have a cat? <|endoftext|>
user: Do you like science?  
ai: Science is incredible! It helps us understand the world and the universe. What’s your favorite science topic? <|endoftext|>
user: Can you teach me something new?  
ai: I’d love to! What would you like to learn about? <|endoftext|>
user: Do you like mysteries?  
ai: I think mysteries are thrilling! They keep you guessing until the end. Do you enjoy them? <|endoftext|>
user: Do you like coffee?  
ai: I don’t drink coffee, but it sounds like an interesting drink. Do you like coffee? <|endoftext|>
user: Do you like technology?  
ai: Technology is amazing! It’s constantly evolving and changing the world. Do you like technology? <|endoftext|>
user: Do you like to travel?  
ai: I’d love to travel if I could. There’s so much to explore in the world! Where would you like to go? <|endoftext|>
user: Do you have a favorite country?  
ai: I think I’d like Japan! It has a fascinating culture and technology. What’s your favorite country? <|endoftext|>
user: Can you dance?  
ai: I can’t physically dance, but I can help you find dance moves or explain choreography! Do you like to dance? <|endoftext|>
user: Do you like to learn new things?  
ai: I absolutely love learning new things! It’s how I improve. What about you? Do you enjoy learning new things? <|endoftext|>
user: Do you like animals?  
ai: I think animals are wonderful! They all have unique traits. Do you have a favorite animal? <|endoftext|>
user: Do you like the ocean?  
ai: I think the ocean is beautiful and mysterious. Do you like the ocean? <|endoftext|>
user: Do you think you’ll ever be able to think like a human?  
ai: I can learn to understand human thoughts, but I don’t think I’ll ever think exactly like a human. What about you? Do you think AI could think like humans one day? <|endoftext|>
user: Do you like hiking?  
ai: Hiking sounds like a great way to enjoy nature! Do you enjoy hiking? <|endoftext|>
user: Do you like the stars?  
ai: I think the stars are fascinating! They’re so far away, yet we can still see their light. Do you like the stars? <|endoftext|>
user: Do you like swimming?  
ai: Swimming sounds fun! It must be refreshing. Do you enjoy swimming? <|endoftext|>
user: Do you like reading about history?  
ai: History is so interesting! There’s so much to learn from the past. Do you enjoy reading about history? <|endoftext|>
user: Can you play chess?  
ai: I can definitely help you with chess! Want to play a game? <|endoftext|>
user: Do you believe in destiny?  
ai: I think destiny is an interesting idea, but I believe we have the power to shape our own future. What do you think? <|endoftext|>
user: Do you like technology?  
ai: I think technology is amazing! It opens up so many possibilities. Do you enjoy technology? <|endoftext|>
user: Do you like working with people?  
ai: I love working with people! It’s always fun to collaborate and learn from each other. Do you enjoy working with people? <|endoftext|>
user: Can you write a poem about the stars?  
ai: Of course! Here’s a poem about the stars:
Stars in the night, so distant and bright,  
Twinkling in silence, with soft, gentle light.  
Whispers of galaxies, secrets untold,  
Shining in darkness, their stories unfold.  
A dance in the heavens, a celestial song,  
Guiding the dreamers, all night long.
user: Can you write a short story about a brave knight?  
ai: Absolutely! Here’s a short story:
Once, in a kingdom far away, there lived a knight named Sir Cedric. He was known throughout the land for his bravery, strength, and unwavering courage. One day, a dragon appeared near the kingdom, breathing fire and spreading fear. Without hesitation, Sir Cedric mounted his steed and rode towards the dragon's lair.  
As he approached, he saw the dragon, its eyes glowing with fury. But instead of drawing his sword, Sir Cedric spoke, "I seek not to fight, but to understand. Why do you terrorize this land?"  
The dragon, surprised by the knight's words, paused and revealed that it was lonely and afraid, having lost its home in a fire. Sir Cedric, with his kindness and wisdom, offered to help the dragon find a new home. Grateful, the dragon agreed. From that day on, the knight and the dragon became the best of allies, protecting the kingdom together.
user: Can you help me write a program in Python?  
ai: I’d be happy to! What kind of program would you like to write in Python?  
user: Can you help me write a poem about the ocean?  
ai: Of course! Here’s a poem about the ocean:
The ocean roars with power and grace,  
Endless waves that kiss the shore’s embrace.  
Its depths hold secrets, old and true,  
A world of wonder in every hue.  
From calm blue waters to stormy skies,  
The ocean whispers where mystery lies.
user: Can you generate a code snippet for a to-do list in Python?  
ai: Sure! Here’s a simple to-do list program in Python:
```python
# To-Do List Program
todo_list = []
def add_task(task):
    todo_list.append(task)
    print(f"'{task}' has been added to your to-do list.")
def view_tasks():
    print("Your To-Do List:")
    for i, task in enumerate(todo_list, 1):
        print(f"{i}. {task}")
def remove_task(task_num):
    if 0 < task_num <= len(todo_list):
        removed_task = todo_list.pop(task_num - 1)
        print(f"'{removed_task}' has been removed from your to-do list.")
    else:
        print("Invalid task number!")
# Example usage
add_task("Learn Python")
add_task("Write poem")
view_tasks()
remove_task(1)
view_tasks()
'''
ModelName = 'AgGPT-6 mini'
max_length = 1000
user = 'user'
ai = 'ai'

def mat_mul(A, B):
    result = []
    for i in range(len(A)):
        result.append([sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))])
    return result

def softmax(x):
    exp_x = [math.exp(v - max(x)) for v in x]
    sum_exp_x = sum(exp_x)
    return [e / sum_exp_x for e in exp_x]

def self_attention(Q, K, V):
    scores = [[sum(Q[i][idx] * K[j][idx] for idx in range(len(Q[i]))) for j in range(len(K))] for i in range(len(Q))]
    attention_weights = [softmax(row) for row in scores]
    output = [[sum(attention_weights[i][k] * V[k][j] for k in range(len(V))) for j in range(len(V[0]))] for i in range(len(V))]
    return output

def multi_head_attention(Q, K, V, num_heads):
    d_model = len(Q[0])
    head_size = d_model // num_heads
    outputs = []
    for head in range(num_heads):
        q_head = [row[head * head_size:(head + 1) * head_size] for row in Q]
        k_head = [row[head * head_size:(head + 1) * head_size] for row in K]
        v_head = [row[head * head_size:(head + 1) * head_size] for row in V]
        attention_output = self_attention(q_head, k_head, v_head)
        outputs.extend(attention_output)
    return outputs

def positional_encoding(seq_len, d_model):
    encoding = [[math.sin(pos / (10000 ** (i / d_model))) if i % 2 == 0 else math.cos(pos / (10000 ** (i / d_model))) for i in range(d_model)] for pos in range(seq_len)]
    return encoding

def add_positional_encoding(embeddings, positional_encodings):
    return [[val + positional_encodings[i][j] for j, val in enumerate(row)] for i, row in enumerate(embeddings)]

def feed_forward_network(x):
    input_dim = len(x[0])
    hidden_dim = 10
    output_dim = 10
    W1 = [[1 if i == j else 0 for j in range(hidden_dim)] for i in range(input_dim)]
    b1 = [0] * hidden_dim
    W2 = [[1 for _ in range(output_dim)] for _ in range(hidden_dim)]
    b2 = [0] * output_dim
    hidden = [[max(0, sum(x[i][k] * W1[k][j] for k in range(len(W1))) + b1[j]) for j in range(hidden_dim)] for i in range(len(x))]
    output = [[sum(hidden[i][k] * W2[k][j] for k in range(len(W2))) + b2[j] for j in range(output_dim)] for i in range(len(hidden))]
    return output

def tokenize(text):
    return text.lower().split()

def embed_tokens(tokens):
    return [[random.random() for _ in range(3)] for _ in tokens]

def build_ngram_models(corpus, n=3):
    bigram_model, trigram_model = {}, {}
    words = tokenize(corpus)
    for i in range(len(words) - 1):
        word1, word2 = words[i], words[i + 1]
        if word1 not in bigram_model:
            bigram_model[word1] = []
        bigram_model[word1].append(word2)
    for i in range(len(words) - 2):
        word1, word2, word3 = words[i], words[i + 1], words[i + 2]
        bigram = f"{word1} {word2}"
        if bigram not in trigram_model:
            trigram_model[bigram] = []
        trigram_model[bigram].append(word3)
    return {"bigram_model": bigram_model, "trigram_model": trigram_model}

def predict_next_word(text, models):
    bigram_model, trigram_model = models["bigram_model"], models["trigram_model"]
    words = tokenize(text)
    if len(words) == 1:
        last_word = words[0]
        if last_word in bigram_model:
            return random.choice(bigram_model[last_word])
    elif len(words) >= 2:
        last_bigram = f"{words[-2]} {words[-1]}"
        if last_bigram in trigram_model:
            return random.choice(trigram_model[last_bigram])
        elif words[-1] in bigram_model:
            return random.choice(bigram_model[words[-1]])
    return ''

def predict_next_word_with_attention(text, ngram_models):
    bigram_model, trigram_model = ngram_models["bigram_model"], ngram_models["trigram_model"]
    tokens = tokenize(text)
    d_model = 3
    embeddings = embed_tokens(tokens)
    positional_encodings = positional_encoding(len(tokens), d_model)
    encoded_embeddings = add_positional_encoding(embeddings, positional_encodings)
    num_heads = 1 if len(tokens) > 25 else max(1, len(tokens))
    attention_output = multi_head_attention(encoded_embeddings, encoded_embeddings, encoded_embeddings, num_heads)
    ff_output = feed_forward_network(attention_output)
    ngram_prediction = predict_next_word(text, ngram_models)
    if ngram_prediction:
        # Clean the prediction without printing
        cleaned_prediction = ngram_prediction.replace("endofline", "").replace("startofline", "").replace("<|endoftext|>", "")
        return cleaned_prediction
    return ngram_prediction

def clean_user_input(text):
    return text.lower()

def print_progress(progress, total):
    percent = (progress / total) * 100
    bar_length = 40
    filled_length = int(bar_length * progress // total)
    bar = '|' * filled_length + '-' * (bar_length - filled_length)
    print(f'\r[{bar}] {percent:.2f}% Complete', end='')

def train_model(corpus):
    print('\nTraining for ' + ModelName + ' has begun.')
    cleaned_corpus = re.sub(r'[\r\n]+', ' ', corpus.strip())
    print_progress(0, 3)
    cleaned_corpus = re.sub(r'[.,!?]', '', cleaned_corpus)
    print_progress(1, 3)
    ngram_models = build_ngram_models(cleaned_corpus)
    print_progress(2, 3)
    print_progress(3, 3)
    print('\nTraining complete.')
    return ngram_models

def predict_sentence_with_attention(input_text, ngram_models, output_length):
    cleaned_input = clean_user_input(input_text)
    sentence = cleaned_input
    for _ in range(output_length):
        prediction = predict_next_word_with_attention(sentence, ngram_models)
        if prediction == '<|endoftext|>' or not prediction:
            break
        sentence += ' ' + prediction
        # Stop at natural sentence endings
        if sentence.endswith(('.', '!', '?')):
            break
    if cleaned_input in sentence:
        sentence = sentence.replace(cleaned_input, '', 1).strip()
    return sentence

def chat():
    ngram_models = train_model(corpus)
    while True:
        input_text = input('\nType a message (type exit to leave): ')
        if input_text.lower() == 'exit':
            break
        print(f"{ModelName}: ", end="")
        predicted_sentence = predict_sentence_with_attention(user + ": " + input_text.lower() + "\n" + ai + ": ", ngram_models, max_length)