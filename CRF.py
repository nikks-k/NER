import docx
import nltk
import sklearn_crfsuite

nltk.download('punkt_tab')


# Функция, которую вы привели для извлечения жирным выделённых сущностей
def extract_bold_entities(docx_file):
    doc = docx.Document(docx_file)
    bold_entities = []
    for para in doc.paragraphs:
        current_entity = ""
        in_entity = False
        for run in para.runs:
            if run.bold:
                if not in_entity:
                    current_entity = run.text
                    in_entity = True
                else:
                    current_entity += run.text
            else:
                if in_entity and run.text.strip() == "":
                    current_entity += run.text
                else:
                    if in_entity:
                        bold_entities.append(current_entity.strip())
                        current_entity = ""
                        in_entity = False
        if in_entity:
            bold_entities.append(current_entity.strip())
    return bold_entities

# Пример: извлечение сущностей из документа
docx_file = './texts/том_1_часть_1.docx'  # замените на путь к вашему файлу
bold_entities = extract_bold_entities(docx_file)
print("Извлеченные сущности:", bold_entities)

# Далее, для создания обучающего набора:
# Предположим, у нас есть функция, которая разбивает весь текст на токены и создаёт BIO-разметку.
# Ниже — упрощённый пример:

def create_bio_tags(text, bold_entities):
    tokens = nltk.word_tokenize(text)
    bio_tags = ['O'] * len(tokens)
    
    for entity in bold_entities:
        entity_tokens = nltk.word_tokenize(entity)
        # Поиск последовательности entity_tokens в tokens
        for i in range(len(tokens) - len(entity_tokens) + 1):
            if tokens[i:i+len(entity_tokens)] == entity_tokens:
                bio_tags[i] = 'B-PER'
                for j in range(1, len(entity_tokens)):
                    bio_tags[i+j] = 'I-PER'
                # Предположим, что сущность не встречается повторно, либо используем дополнительную обработку
                break
    return list(zip(tokens, bio_tags))

# Допустим, полный текст документа читается отдельно
full_text = "./texts/Чистый фрагмент.docx"  # Здесь ваш полный текст из документа
training_data = create_bio_tags(full_text, bold_entities)

# Функции для извлечения признаков (как ранее)
def word2features(sent, i):
    word = sent[i]
    features = {
        'bias': 1.0,
        'word.lower()': word.lower(),
        'word.istitle()': word.istitle(),
        'word.isupper()': word.isupper(),
        'word.isdigit()': word.isdigit(),
    }
    if i > 0:
        word_prev = sent[i-1]
        features.update({
            '-1:word.lower()': word_prev.lower(),
            '-1:word.istitle()': word_prev.istitle(),
            '-1:word.isupper()': word_prev.isupper(),
        })
    else:
        features['BOS'] = True
    if i < len(sent)-1:
        word_next = sent[i+1]
        features.update({
            '+1:word.lower()': word_next.lower(),
            '+1:word.istitle()': word_next.istitle(),
            '+1:word.isupper()': word_next.isupper(),
        })
    else:
        features['EOS'] = True
    return features

def sent2features(sent):
    tokens = [token for token, label in sent]
    return [word2features(tokens, i) for i in range(len(tokens))]

def sent2labels(sent):
    return [label for token, label in sent]

# Обучающие данные должны быть разделены на предложения. Здесь для простоты обрабатываем один кусок.
X_train = [sent2features(training_data)]
y_train = [sent2labels(training_data)]

# Обучаем модель CRF
crf = sklearn_crfsuite.CRF(
    algorithm='lbfgs',
    c1=0.1,
    c2=0.1,
    max_iterations=100,
    all_possible_transitions=True
)
crf.fit(X_train, y_train)

# Применяем модель к новому тексту
test_text = "Пётр Ильич Пушкин родился в Москве."
test_tokens = nltk.word_tokenize(test_text)
test_sent = list(zip(test_tokens, ["O"]*len(test_tokens)))
X_test = sent2features(test_sent)
y_pred = crf.predict_single(X_test)

print("Предсказанные метки:")
for token, label in zip(test_tokens, y_pred):
    print(f"{token}: {label}")