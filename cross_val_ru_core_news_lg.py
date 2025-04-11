import json
import random
import spacy
from spacy.util import minibatch
from spacy.training import Example
from spacy.scorer import Scorer
from sklearn.model_selection import KFold
import numpy as np
import copy

# Загружаем обучающие данные из JSON-файла
with open("training_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Определяем число fold-ов для кросс-валидации
n_splits = 5
kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)

# Списки для сохранения метрик по fold-ам
all_precisions = []
all_recalls = []
all_fscores = []

# Для сохранения лучшей модели
best_fscore = 0.0
best_model = None

# Преобразуем данные в список индексов
data = list(data)
data = np.array(data)

fold = 1
for train_index, val_index in kf.split(data):
    print(f"\n--- Fold {fold} ---")
    
    train_data = data[train_index].tolist()
    val_data = data[val_index].tolist()
    
    # Загружаем исходную модель для каждого fold-а
    nlp = spacy.load("ru_core_news_lg")
    
    # Добавляем компонент NER, если его нет
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner")
    else:
        ner = nlp.get_pipe("ner")
    
    # Добавляем метки из обучающей выборки
    for text, annotations in train_data:
        for ent in annotations["entities"]:
            ner.add_label(ent[2])
    
    # Отключаем остальные пайпы для ускорения обучения
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes):
        optimizer = nlp.begin_training()
        epochs = 20  # Можно увеличить число эпох, если данных мало
        for epoch in range(epochs):
            random.shuffle(train_data)
            losses = {}
            batches = minibatch(train_data, size=2)
            for batch in batches:
                examples = []
                for text, annotations in batch:
                    doc = nlp.make_doc(text)
                    example = Example.from_dict(doc, annotations)
                    examples.append(example)
                nlp.update(examples, drop=0.5, losses=losses)
            print(f"Fold {fold}, Epoch {epoch+1}: Losses: {losses}")
    
    # Оценка на валидационном наборе
    val_examples = []
    for text, annotations in val_data:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        val_examples.append(example)
    
    val_scores = nlp.evaluate(val_examples)
    precision = val_scores.get("ents_p", 0.0)
    recall = val_scores.get("ents_r", 0.0)
    fscore = val_scores.get("ents_f", 0.0)
    
    print(f"Fold {fold}: Precision: {precision:.3f}, Recall: {recall:.3f}, F1: {fscore:.3f}")
    
    all_precisions.append(precision)
    all_recalls.append(recall)
    all_fscores.append(fscore)
    
    # Если fscore для текущей fold-итерации лучше, сохраняем копию модели
    if fscore > best_fscore:
        best_fscore = fscore
        best_model = copy.deepcopy(nlp)
    
    fold += 1

# Усредняем метрики по всем fold-ам
avg_precision = np.mean(all_precisions)
avg_recall = np.mean(all_recalls)
avg_fscore = np.mean(all_fscores)

print("\n=== Cross-Validation Results ===")
print(f"Average Precision: {avg_precision:.3f}")
print(f"Average Recall:    {avg_recall:.3f}")
print(f"Average F1:        {avg_fscore:.3f}")
print(f"Best F1 from folds: {best_fscore:.3f}")

# Сохраняем лучшую модель на диск
if best_model is not None:
    best_model.to_disk("best_model_ru_ner")
    print("Лучшая модель сохранена в папку 'best_model_ru_ner'.")
else:
    print("Модель не была обучена.")

# Пример тестирования сохранённой модели
test_nlp = spacy.load("best_model_ru_ner")
test_texts = [
    'Несмотря на нерусскую местность и обстановку: фруктовые сады, каменные ограды, черепичные крыши, горы, видневшиеся вдали, — на нерусский народ, с любопытством смотревший на солдат, — полк имел точно такой же вид, какой имел всякий русский полк.',
    'Кутузов вёл переговоры с представителями Кремля.'
]
for text in test_texts:
    doc = test_nlp(text)
    print(f"\nTest Text: {text}")
    for ent in doc.ents:
        print(f"  - {ent.text} ({ent.label_})")
