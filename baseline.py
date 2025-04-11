# --- вариант 1
# texts = [
#     ("В октябре 1805 года русские войска занимали села и города эрцгерцогства Австрийского, и еще новые полки приходили из России, и, отягощая постоем жителей, располагались у крепости Браунау.", {"entities": [(58, 71, "GPE"), (72, 84, "GPE"), (117, 123, "GPE"), (179, 186, "GPE")]}),
#     ("К Кутузову накануне прибыл член гофкригсрата из Вены, с предложениями и требованиями идти как можно скорее на соединение с армией эрцгерцога Фердинанда и Мака, и Кутузов, не считавший выгодным это соединение, в числе прочих доказательств в пользу своего мнения намеревался показать австрийскому генералу то печальное положение, в котором приходили войска из России.", {"entities": [(2, 10, "PER"), (48, 52, "GPE"), (141, 151, "PER"), (154, 158, "PER"), (162, 169, "PER")]})
# ]

# nlp = spacy.load("ru_core_news_lg")

# if 'ner' not in nlp.pipe_names:
#     ner = nlp.add_pipe('ner')
# else:
#     ner = nlp.get_pipe('ner')

# for _, annotations in texts:
#     for ent in annotations['entities']:
#         if ent not in ner.labels:
#             ner.add_label(ent[2])

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
#                 docum = nlp.make_doc(text)
#                 example = Example.from_dict(docum, annotations)
#                 examples.append(example)
#             nlp.update(examples, drop=0.5, losses=losses)
#         print(f'Epoch: {epoch + 1}, Losses: {losses}')



# nlp.to_disk("voina_i_mir")

# translate_nlp = spacy.load("voina_i_mir")

# test_texts = [
#     'Несмотря на нерусскую местность и обстановку: фруктовые сады, каменные ограды, черепичные крыши, горы, видневшиеся вдали, — на нерусский народ, с любопытством смотревший на солдат, — полк имел точно такой же вид, какой имел всякий русский полк, готовившийся к смотру где-нибудь в середине России.',
#     'Сначала Кутузов стоял на одном месте, пока полк двигался; потом Кутузов рядом с белым генералом, пешком, сопутствуемый свитою, стал ходить по рядам.'
# ]

# for text in test_texts:
#     docum = translate_nlp(text)
#     print(f'Text: {text}')
#     print('Entities:', [(ent.text, ent.label_) for ent in docum.ents])


# text = "— Покорно благодарю, я теперь один проеду, — сказал князь Андрей, желая избавиться от штаб-офицера, — не беспокойтесь, пожалуйста."
# doc = nlp.make_doc(text)
# for token in doc:
#     print(f"Токен: '{token.text}', начало: {token.idx}, конец: {token.idx + len(token.text)}")

# biluo_tags = spacy.training.offsets_to_biluo_tags(doc, [(2, 10, "PER"), (48, 52, "GPE"), (141, 151, "PER"), (154, 158, "PER"), (162, 169, "PER")])
# print(biluo_tags)

