from docx import Document

import random

import spacy
from spacy.util import minibatch
from spacy.training.example import Example
import re
import json


# def load_annotations(filename):
#     """
#     Загружает аннотации из файла, где каждая строка имеет формат:
#     <слово или словосочетание> <метка>
#     Пример:
#         Франц PER
#         Кремса GPE
#     Возвращает словарь {entity_text: label, ...}
#     """
#     annotations = {}
#     with open(filename, encoding='utf-8') as f:
#         for line in f:
#             line = line.strip()
#             if not line:
#                 continue
#             parts = line.split()
#             if len(parts) >= 2:
#                 label = parts[-1]
#                 entity_text = " ".join(parts[:-1])
#                 annotations[entity_text.strip()] = label
#     return annotations

# def split_into_sentences(text):
#     """
#     Разбивает текст на предложения по следующим правилам:
#     - Если в тексте присутствуют пустые строки, то они означают границу между предложениями.
#     - Предложение считается завершённым, если в конце стоит точка (.), восклицательный (!) или вопросительный знак (?),
#       либо последовательность точек (например, "..." и более).
    
#     Возвращает список кортежей (sentence, start, end), где start и end – позиции предложения в тексте.
#     """
#     sentences = []
#     start = 0
#     # Регулярное выражение ищет окончания предложений
#     for match in re.finditer(r'([.!?…]+)(\s+|$)', text):
#         end = match.end()
#         sentence = text[start:end].strip()
#         if sentence:
#             sentences.append((sentence, start, end))
#         start = end
#     if start < len(text):
#         sentence = text[start:].strip()
#         if sentence:
#             sentences.append((sentence, start, len(text)))
#     return sentences

# def extract_training_data(docx_filename, annotations_dict):
#     """
#     Извлекает обучающие данные из DOCX-файла.
#     Для каждого абзаца (paragraph) происходит следующее:
#       - Разбивается на предложения по правилам (пустая строка = граница, окончание знаками препинания).
#       - Для каждого run-а абзаца, если он жирный, дополнительно разбивается по непустым последовательностям (с помощью re.finditer).
#       - Для каждого найденного слова (или словосочетания) проверяется, есть ли оно в аннотациях.
#       - Если слово найдено в аннотациях, вычисляются его абсолютные смещения относительно абзаца и затем пересчитываются для каждого предложения.
      
#     Возвращает список примеров вида:
#       (sentence_text, {"entities": [(start, end, label), ...]})
#     """
#     document = docx.Document(docx_filename)
#     training_data = []

#     for para in document.paragraphs:
#         # Пропускаем пустые абзацы
#         if not para.text.strip():
#             continue

#         para_text = para.text
#         bold_entities = []
#         current_index = 0  # абсолютное смещение в абзаце
#         for run in para.runs:
#             run_text = run.text
#             run_length = len(run_text)
#             if run.bold and run_text.strip():
#                 # Если в одном run-е несколько слов, разбиваем их по непробельным последовательностям
#                 for m in re.finditer(r'\S+', run_text):
#                     token_text = m.group()
#                     token_start = current_index + m.start()
#                     token_end = current_index + m.end()
#                     if token_text in annotations_dict:
#                         label = annotations_dict[token_text]
#                         bold_entities.append((token_start, token_end, label))
#                     else:
#                         print(f"Warning: Не найдена аннотация для сущности '{token_text}'")
#             current_index += run_length

#         # Разбиваем абзац на предложения с указанием позиций внутри абзаца
#         sentences = split_into_sentences(para_text)
#         for sentence, sent_start, sent_end in sentences:
#             sentence_entities = []
#             for ent_start, ent_end, label in bold_entities:
#                 # Если сущность полностью находится в пределах предложения,
#                 # пересчитываем смещения относительно начала предложения.
#                 if ent_start >= sent_start and ent_end <= sent_end:
#                     sentence_entities.append((ent_start - sent_start, ent_end - sent_start, label))
#             if sentence_entities:
#                 training_data.append((sentence, {"entities": sentence_entities}))
#     return training_data

# if __name__ == '__main__':
#     # Пути к файлам
#     docx_file = "./texts/entities.docx"             # DOCX-файл с текстом, где сущности выделены жирным
#     annotations_file = "./texts/entities_tagged.txt"  # Файл с аннотациями вида:
#                                           # Франц PER
#                                           # Кремса GPE
#                                           # Дюренштейне GPE
#                                           # Дюренштейна GPE
#                                           # орденом REW
#                                           # Марии-Терезии REW
#                                           # 3-й REW
#     output_file = "training_data.json"

#     annotations_dict = load_annotations(annotations_file)
#     print("Загруженные аннотации:")
#     print(json.dumps(annotations_dict, ensure_ascii=False, indent=4))

#     training_data = extract_training_data(docx_file, annotations_dict)
#     print("Обучающие данные:")
#     print(json.dumps(training_data, ensure_ascii=False, indent=4))

#     with open(output_file, "w", encoding="utf-8") as f:
#         json.dump(training_data, f, ensure_ascii=False, indent=4)


# # Загрузить обучающие данные из JSON-файла
# with open("training_data.json", "r", encoding="utf-8") as f:
#     texts = json.load(f)

# # Создаем или загружаем модель spaCy
# nlp = spacy.load("ru_core_news_lg")

# # Добавляем компонент NER, если его нет
# if 'ner' not in nlp.pipe_names:
#     ner = nlp.add_pipe("ner")
# else:
#     ner = nlp.get_pipe("ner")

# # Добавляем метки из обучающих данных
# for _, annotations in texts:
#     for ent in annotations['entities']:
#         ner.add_label(ent[2])

# # Отключаем все пайпы кроме 'ner' для ускорения обучения
# other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
# with nlp.disable_pipes(*other_pipes):
#     optimizer = nlp.begin_training()
#     epochs = 50
#     for epoch in range(epochs):
#         random.shuffle(texts)
#         losses = {}
#         batches = minibatch(texts, size=2)
#         for batch in batches:
#             examples = []
#             for text, annotations in batch:
#                 doc = nlp.make_doc(text)
#                 example = Example.from_dict(doc, annotations)
#                 examples.append(example)
#             nlp.update(examples, drop=0.5, losses=losses)
#         print(f'Epoch: {epoch + 1}, Losses: {losses}')

# # Сохраняем обученную модель
# nlp.to_disk("voina_i_mir")

# # Загружаем модель для тестирования
# translate_nlp = spacy.load("voina_i_mir")

# test_texts = [
#     'Несмотря на нерусскую местность и обстановку: фруктовые сады, каменные ограды, черепичные крыши, горы, видневшиеся вдали, — на нерусский народ, с любопытством смотревший на солдат, — полк имел точно такой же вид, какой имел всякий русский полк, готовившийся к смотру где-нибудь в середине России.',
#     'Сначала Кутузов стоял на одном месте, пока полк двигался; потом Кутузов рядом с белым генералом, пешком, сопутствуемый свитою, стал ходить по рядам.',\
#     'Князь Андрей о Наташе:',
#     'Пьер Безухов: ничего не найдено, ничего не придумано. Знать мы можем только то, что ничего не знаем. И это высшая степень человеческой премудрости.',
#     'Наполеон:',
#     'От великого до смешного только шаг.',
#     'Уж на что Суворова — и того расколотили.',
#     'Мария Болконская:', 
#     'Христос, сын бога, сошел на землю и сказал нам, что эта жизнь есть мгновенная жизнь, испытание, а мы все держимся за нее и думаем в ней найти счастье. Как никто не понял этого?',
#     'А я так убежден и, основываясь на последнем письме, которым почтил меня его высочество эрцгерцог Фердинанд, предполагаю, что австрийские войска, под начальством столь искусного помощника, каков генерал Мак, теперь уже одержали решительную победу и не нуждаются более в нашей помощи, — сказал Кутузов.'
# ]

# for text in test_texts:
#     doc = translate_nlp(text)
#     print(f'Text: {text}')
#     print('Entities:', [(ent.text, ent.label_) for ent in doc.ents])


import json
import random
import spacy
from spacy.util import minibatch
from spacy.training import Example
from spacy.scorer import Scorer

# Загрузка обучающих данных из JSON-файла
with open("training_data.json", "r", encoding="utf-8") as f:
    texts = json.load(f)

# Перемешиваем данные и разделяем на тренировочную (80%) и валидационную (20%) выборки
random.shuffle(texts)
split = int(0.8 * len(texts))
train_texts = texts[:split]
val_texts = texts[split:]

# Загружаем модель (например, ru_core_news_lg)
nlp = spacy.load("ru_core_news_lg")

# Добавляем компонент NER, если его нет
if "ner" not in nlp.pipe_names:
    ner = nlp.add_pipe("ner")
else:
    ner = nlp.get_pipe("ner")

# Добавляем метки из тренировочной выборки
for _, annotations in train_texts:
    for ent in annotations["entities"]:
        ner.add_label(ent[2])

# Отключаем остальные пайпы для ускорения обучения
other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
with nlp.disable_pipes(*other_pipes):
    optimizer = nlp.begin_training()
    
    epochs = 50
    best_f1 = 0.0
    patience = 5  # Количество эпох для ожидания улучшения
    patience_counter = 0
    
    for epoch in range(epochs):
        random.shuffle(train_texts)
        losses = {}
        batches = minibatch(train_texts, size=2)
        for batch in batches:
            examples = []
            for text, annotations in batch:
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)
                examples.append(example)
            nlp.update(examples, drop=0.5, losses=losses)
        
        # Оценка на валидационной выборке
        val_examples = []
        for text, annotations in val_texts:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            val_examples.append(example)
        val_scores = nlp.evaluate(val_examples)
        precision = val_scores.get("ents_p", 0.0)
        recall = val_scores.get("ents_r", 0.0)
        fscore = val_scores.get("ents_f", 0.0)
        
        print(f"Epoch: {epoch+1}, Losses: {losses}, Precision: {precision:.3f}, Recall: {recall:.3f}, F1: {fscore:.3f}")
        
        # Механизм ранней остановки
        if fscore > best_f1:
            best_f1 = fscore
            patience_counter = 0
        else:
            patience_counter += 1
        
        if patience_counter >= patience:
            print("Early stopping triggered: no improvement in F1 for", patience, "epochs.")
            break

# Сохраняем обученную модель
nlp.to_disk("voina_i_mir")

# Тестирование модели на примерах
translate_nlp = spacy.load("voina_i_mir")

test_texts = [
    'Несмотря на нерусскую местность и обстановку: фруктовые сады, каменные ограды, черепичные крыши, горы, видневшиеся вдали, — на нерусский народ, с любопытством смотревший на солдат, — полк имел точно такой же вид, какой имел всякий русский полк, готовившийся к смотру где-нибудь в середине России.',
    'Сначала Кутузов стоял на одном месте, пока полк двигался; потом Кутузов рядом с белым генералом, пешком, сопутствуемый свитою, стал ходить по рядам.',\
    'Князь Андрей о Наташе:',
    'Пьер Безухов: ничего не найдено, ничего не придумано. Знать мы можем только то, что ничего не знаем. И это высшая степень человеческой премудрости.',
    'Наполеон:',
    'От великого до смешного только шаг.',
    'Уж на что Суворова — и того расколотили.',
    'Мария Болконская:', 
    'Христос, сын бога, сошел на землю и сказал нам, что эта жизнь есть мгновенная жизнь, испытание, а мы все держимся за нее и думаем в ней найти счастье. Как никто не понял этого?',
    'А я так убежден и, основываясь на последнем письме, которым почтил меня его высочество эрцгерцог Фердинанд, предполагаю, что австрийские войска, под начальством столь искусного помощника, каков генерал Мак, теперь уже одержали решительную победу и не нуждаются более в нашей помощи, — сказал Кутузов.'
]

for text in test_texts:
    doc = translate_nlp(text)
    print(f"Text: {text}")
    print("Entities:", [(ent.text, ent.label_) for ent in doc.ents])


