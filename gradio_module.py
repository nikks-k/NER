import gradio as gr
import spacy

# Загружаем модель spaCy; убедитесь, что "voina_i_mir" доступна
nlp = spacy.load("voina_i_mir")

def predict(text):
    # Передаём текст в модель spaCy
    doc = nlp(text)
    
    # Формируем ответ: если сущности обнаружены, выводим их, иначе информируем об отсутствии
    if doc.ents:
        result = "\n".join([f"{ent.text}: {ent.label_}" for ent in doc.ents])
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

# Создаем интерфейс, используя обновленные компоненты gradio
demo = gr.Interface(
    fn=predict,
    inputs=gr.Textbox(lines=4, placeholder="Введите текст для анализа..."),
    outputs=gr.Textbox(label="Результат"),
    css=custom_css,
    title="Интерфейс spaCy-модели",
)

demo.launch(share=True)
