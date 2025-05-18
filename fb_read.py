from xml.etree import ElementTree as ET
from nltk.tokenize import sent_tokenize
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(
    "Qwen/Qwen-7B", trust_remote_code=True
)

def parse_fb2(path: str) -> str:
    tree = ET.parse(path)
    paragraphs = []
    for elem in tree.iter():
        if elem.tag.endswith('p') and elem.text:
            paragraphs.append(elem.text.strip())
    return "\n".join(paragraphs)
def chunk_by_sentences_with_word_split(
    text: str,
    max_tokens: int = 2000,
    log_path: str = "long_sentences_chunks.txt"
):
    sentences = sent_tokenize(text, language="russian")
    chunks = []
    current_chunk = []
    current_count = 0

    with open(log_path, "w", encoding="utf-8") as log_file:
        for sent in sentences:
            all_tokens = tokenizer.encode(sent, add_special_tokens=False)
            if len(all_tokens) > max_tokens:
                # Логируем само предложение
                log_file.write(f"\n[Long sentence: {len(all_tokens)} tokens]\n{sent}\n")

                # Разбираем на субчанки по словам
                words = sent.split()
                subchunk_words = []
                subcount = 0

                for w in words:
                    w_toks = tokenizer.encode(" " + w, add_special_tokens=False)
                    w_len = len(w_toks)

                    # Если слово само слишком длинное — делим по токенам
                    if w_len > max_tokens:
                        # Сначала сбросим накопленный субчанк
                        if subchunk_words:
                            text_part = " ".join(subchunk_words)
                            chunks.append(text_part)        # <-- добавляем в общий список
                            subchunk_words, subcount = [], 0
                        # fallback: режем слово по токенам
                        for i in range(0, w_len, max_tokens):
                            part = w_toks[i : i + max_tokens]
                            part_text = tokenizer.decode(part, skip_special_tokens=True)
                            chunks.append(part_text)       # <-- добавляем в общий список
                            log_file.write(f"  Fallback subchunk ({len(part)}) tokens:\n{part_text}\n")
                        continue

                    # Обычное накапливание слов в субчанк
                    if subcount + w_len <= max_tokens:
                        subchunk_words.append(w)
                        subcount += w_len
                    else:
                        # Сброс текущего субчанка
                        text_part = " ".join(subchunk_words)
                        chunks.append(text_part)        # <-- добавляем в общий список
                        log_file.write(f"  Subchunk ({subcount} tokens):\n{text_part}\n")
                        # Начинаем новый
                        subchunk_words, subcount = [w], w_len

                # Записываем последний субчанк этого предложения
                if subchunk_words:
                    text_part = " ".join(subchunk_words)
                    chunks.append(text_part)            # <-- и его тоже
                    log_file.write(f"  Subchunk ({subcount} tokens):\n{text_part}\n")

                # Сбрасываем текущий обычный чанк
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk, current_count = [], 0

                continue  # переходим к следующему предложению

            # Обычное поведение для коротких предложений
            sent_len = len(all_tokens)
            if current_count + sent_len <= max_tokens:
                current_chunk.append(sent)
                current_count += sent_len
            else:
                chunks.append(" ".join(current_chunk))
                current_chunk, current_count = [sent], sent_len

        # Не забываем последний чанк
        if current_chunk:
            chunks.append(" ".join(current_chunk))

    return chunks

# Пример использования:
if __name__ == "__main__":
    text = parse_fb2("book/voina-i-mir.fb2")
    chunks = chunk_by_sentences_with_word_split(text, max_tokens=2000)
    print(f"Всего чанков без длинных предложений: {len(chunks)}")
    print("Проверьте файл long_sentences_chunks.txt для субчанков длинных предложений.")


# from nltk.tokenize import sent_tokenize
# from transformers import AutoTokenizer

# tokenizer = AutoTokenizer.from_pretrained(
#     "Qwen/Qwen-7B", trust_remote_code=True
# )

# def parse_fb2(path: str) -> str:
#     tree = ET.parse(path)
#     root = tree.getroot()
#     paragraphs = []
#     for elem in root.iter():
#         if elem.tag.endswith('p') and elem.text:
#             paragraphs.append(elem.text.strip())
#     return "\n".join(paragraphs)

# def chunk_by_sentences(text: str,
#                        max_tokens: int = 2000) -> list[str]:
#     """
#     Разбивает text на чанки по предложениям.
#     Если предложение > max_tokens, режет его по токенам.
#     """
#     # 1. Разбиение на предложения
#     sentences = sent_tokenize(text, language='russian')
#     chunks = []
#     current_chunk = []
#     current_token_count = 0

#     for sent in sentences:
#         sent_tokens = tokenizer.encode(sent, add_special_tokens=False)
#         # 2. Если одно предложение слишком длинное
#         if len(sent_tokens) > max_tokens:
#             # Сначала завершаем текущий чанк
#             if current_chunk:
#                 chunks.append(" ".join(current_chunk))
#                 current_chunk, current_token_count = [], 0
#             # Разрезаем длинное предложение на подчасти
#             for i in range(0, len(sent_tokens), max_tokens):
#                 sub_tokens = sent_tokens[i:i+max_tokens]
#                 chunks.append(tokenizer.decode(
#                     sub_tokens, skip_special_tokens=True
#                 ))
#         # 3. Иначе пробуем добавить предложение в текущий чанк
#         elif current_token_count + len(sent_tokens) <= max_tokens:
#             current_chunk.append(sent)
#             current_token_count += len(sent_tokens)
#         else:
#             # 4. Закрываем текущий чанк и начинаем новый
#             chunks.append(" ".join(current_chunk))
#             current_chunk = [sent]
#             current_token_count = len(sent_tokens)

#     # 5. Добавляем последний чанк
#     if current_chunk:
#         chunks.append(" ".join(current_chunk))

#     return chunks

# def chunk_text(text: str, max_tokens: int = 2000) -> list[str]:
#     return chunk_by_sentences(text, max_tokens=max_tokens)

# path = 'book/voina-i-mir.fb2'
# text = parse_fb2(path)

# # Получаем чанки
# chunks = list(chunk_text(text))

# # Выводим первые три чанка
# for idx, chunk in enumerate(chunks[:2]):
#     print(f"--- Чанк {idx+1} ---\n{chunk}\n")
