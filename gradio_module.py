# import gradio as gr
# import spacy

# # Загружаем модель spaCy; убедитесь, что "voina_i_mir" доступна
# nlp = spacy.load("voina_i_mir")

# def predict(text):
#     # Передаём текст в модель spaCy
#     doc = nlp(text)
    
#     # Формируем ответ: если сущности обнаружены, выводим их, иначе информируем об отсутствии
#     if doc.ents:
#         result = "\n".join([f"{ent.text}: {ent.label_}" for ent in doc.ents])
#     else:
#         result = "Нет распознанных сущностей."
#     return result

# custom_css = """
# /* Изменение фона всего приложения */
# .gradio-container {
#     background-color: #999950 !important;
# }

# /* Изменение цвета кнопки */
# button {
#     background-color: #59351F !important;
#     color: white !important;
#     border: none;
#     border-radius: 4px;
#     padding: 10px 20px;
#     font-size: 16px;
# }
# """

# # Создаем интерфейс, используя обновленные компоненты gradio
# demo = gr.Interface(
#     fn=predict,
#     inputs=gr.Textbox(lines=4, placeholder="Введите текст для анализа..."),
#     outputs=gr.Textbox(label="Результат"),
#     css=custom_css,
#     title="Интерфейс spaCy-модели",
# )

# demo.launch(share=True)

import gradio as gr
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification

# Загрузка токенизатора и модели
tokenizer = AutoTokenizer.from_pretrained("DeepPavlov/rubert-base-cased")
model = AutoModelForTokenClassification.from_pretrained("./rubert-ner/final")  # Укажите путь к вашей модели

def predict(text):
    # Токенизация входного текста с обрезкой при необходимости
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    
    # Получаем предсказания модели
    with torch.no_grad():
        outputs = model(**inputs)
    predictions = outputs.logits
    
    # Определяем наиболее вероятные метки для токенов
    predicted_labels = torch.argmax(predictions, dim=-1).squeeze().tolist()
    tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'].squeeze())
    
    # Инициализация списка для сущностей и переменных для объединения субтокенов
    entities = []
    current_entity = ""
    current_label = None
    
    # Пропускаем специальные токены
    special_tokens = set(tokenizer.all_special_tokens)
    for token, label in zip(tokens, predicted_labels):
        if token in special_tokens:
            continue
        label_name = model.config.id2label[label]
        
        # Если токен не относится к сущности, завершить текущую сущность (если она накапливалась)
        if label_name == "O":
            if current_entity:
                entities.append((current_entity, current_label))
                current_entity = ""
                current_label = None
            continue
        
        # Обработка субтокенов: если токен начинается с "##", объединяем его с предыдущим, если метка совпадает
        if token.startswith("##"):
            if current_entity and current_label == label_name:
                current_entity += token[2:]
            else:
                if current_entity:
                    entities.append((current_entity, current_label))
                current_entity = token[2:]
                current_label = label_name
        else:
            # Если ранее накапливалась сущность, фиксируем её
            if current_entity:
                entities.append((current_entity, current_label))
            current_entity = token
            current_label = label_name
    if current_entity:
        entities.append((current_entity, current_label))
    
    # Формирование выходного результата
    if entities:
        result = "\n".join([f"{ent}: {label}" for ent, label in entities])
    else:
        result = "Нет распознанных сущностей."
    return result

custom_css = """
/* Изменение фона всего приложения */
.gradio-container {
    background-color: #999950 !important;
}

/* Изменение цвета кнопки */
button {
    background-color: #59351F !important;
    color: white !important;
    border: none;
    border-radius: 4px;
    padding: 10px 20px;
    font-size: 16px;
}
"""

# Создаем интерфейс Gradio с указанными компонентами
demo = gr.Interface(
    fn=predict,
    inputs=gr.Textbox(lines=4, placeholder="Введите текст для анализа..."),
    outputs=gr.Textbox(label="Результат"),
    css=custom_css,
    title="Интерфейс NER на основе модели трансформеров",
)

demo.launch(share=True)
