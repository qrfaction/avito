from tqdm import tqdm
import numpy as np
import pandas as pd
import multiprocessing as mlp
from nltk.tokenize.toktok import ToktokTokenizer

def tokenize_worker(sentences):
    tknzr = ToktokTokenizer()
    sentences = [tknzr.tokenize(seq) for seq in tqdm(sentences)]
    return sentences

def tokenize_word(sentences):
    " 多进程分词"
    results = []
    pool = mlp.Pool(mlp.cpu_count())
    aver_t = int(len(sentences)/ mlp.cpu_count()) + 1
    for i in range(mlp.cpu_count()):
        result = pool.apply_async(tokenize_worker,
                                  args=(sentences[i * aver_t:(i + 1) * aver_t],))
        results.append(result)
    pool.close()
    pool.join()

    tokenized_sentences = []
    for result in results:
        tokenized_sentences.extend(result.get())

    return tokenized_sentences

def tokenize_sentences(sentences):

    def step_cal_frequency(sentences):
        frequency = {}
        for sentence in tqdm(sentences):
            for word in sentence:
                if frequency.get(word) is None:
                    frequency[word] = 0
                frequency[word]+=1
        return frequency

    def step_to_seq(sentences,frequency):
        " 句子转序列 "
        words_dict = { }
        seq_list = []

        for sentence in tqdm(sentences):
            seq = []
            for word in sentence:
                if frequency[word]<= 3 :
                    continue
                if word not in words_dict:
                    words_dict[word] = len(words_dict) + 1
                word_index = words_dict[word]
                seq.append(word_index)
            seq_list.append(seq)
        return seq_list,words_dict

    sentences = tokenize_word(sentences)
    freq = step_cal_frequency(sentences)
    return step_to_seq(sentences,freq)


def get_embedding_matrix(word_index):
    print('get embedding matrix')
    from fastText import load_model
    num_words = len(word_index) + 1
    # 停止符用0
    embedding_matrix = np.zeros((num_words,300))

    print('num of word: ',num_words)
    ft_model = load_model('wiki.en.bin')
    for word, i in tqdm(word_index.items()):
        embedding_matrix[i] = ft_model.get_word_vector(word).astype('float32')
    del ft_model

    return embedding_matrix

def pocess_text(data):
    from keras.preprocessing.sequence import pad_sequences
    from config import desc_len,title_len

    desc,word_idx = tokenize_sentences(data['description'].values)
    desc = pad_sequences(desc,maxlen=desc_len,truncating='post')
    desc = np.array(desc)
    desc_embed = get_embedding_matrix(word_idx)

    title,word_idx = tokenize_sentences(data['title'].values)
    title = pad_sequences(title, maxlen=title_len, truncating='post')
    title = np.array(title)
    title_embed = get_embedding_matrix(word_idx)

    return desc,desc_embed,title,title_embed











