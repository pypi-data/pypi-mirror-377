from collections import defaultdict
from pathlib import Path
import numpy as np
import jieba
from ..io.dict import read_yaml_dict
from gensim.models import KeyedVectors
from gensim.scripts.glove2word2vec import glove2word2vec as glove2wv
from nltk.tokenize import word_tokenize
import pandas as pd
from tqdm import tqdm
from prettytable import PrettyTable  # 用于美化表格输出
import multiprocessing
import psutil  # 用于获取系统内存信息
import re
import logging
import platform
from scipy import spatial
from scipy.stats import spearmanr
from typing import List, Set, Optional


# 在文件开头添加
jieba_logger = logging.getLogger('jieba')
jieba_logger.setLevel(logging.CRITICAL)
    
   

def evaluate_analogy(wv, file=None):
    """
    用于评估词向量模型在类比测试（analogy test）中表现的函数。它通过读取指定的类比测试文件，
    计算模型对词语关系预测的准确性，并输出每个类别的准确率、发现词语数量、未发现词语数量以及平均排名等指标。
    
    类比测试的核心是解决形如 "A : B :: C : D" 的问题，翻译过来就是"A之于B，正如C之于D"；
    即通过AB类比关系，找到C的关系词D。该函数通过词向量模型的相似性搜索功能，计算预测结果与真实答案的匹配程度。

    Args:
        wv (KeyedVectors): 词向量模型
        file (str): 测试文件路径，默认使用cntext内置的analogy.txt文件。
    """
    def find_idx_for_word(word, sim_res):
        """
        查找单词在相似结果中的索引位置。
        
        参数:
            word (str): 目标单词。
            sim_res (list of tuples): 相似度结果列表，每个元素为 (word, similarity_score)。
            
        返回:
            tuple: 单词的索引位置和是否找到的指示符。
        """
        for idx, item in enumerate(sim_res):
            if word == item[0]:  # 注意这里我们比较的是单词本身而不是整个元组
                return idx, 1
        return None, 0
    
    res_dict = {}
    ranks = []
    num = 0
    right_pred = 0
    prev_topic = ''
    missing_words_count = 0  # 当前类别的未发现词数
    total_missing_words = {}  # 每个类别的未发现词数统计
    
    if file is None:
        file = Path(__file__).parent / "evaluate_data" / "analogy.txt"
        name = Path(file).stem
        print(f"类比测试: {name}.txt")
        print(file)
    else:
        name = Path(file).stem
        print(f"类比测试: {name}.txt")
    
    with open(file, 'r', encoding='utf-8') as fr:
        lines = fr.readlines()
        for line in tqdm(lines, desc="Processing Analogy Test"):
            line = line.strip()
            if not line or line.startswith(':'):
                if ':' in line:
                    topic = line.split()[1].split('-')[0]
                    if prev_topic and num > 0:
                        res_dict[prev_topic] = {
                            'count': num,
                            'acc': right_pred / num,
                            'average_ranks': np.nanmean(ranks) if ranks else float('nan'),
                            'missing_words': missing_words_count
                        }
                        total_missing_words[prev_topic] = missing_words_count
                    num = 0
                    right_pred = 0
                    ranks = []
                    missing_words_count = 0  # 重置未发现词数计数器
                    prev_topic = topic
                continue
            
            words = line.split()
            if len(words) != 4:
                print(f"{line} is not a valid analogy question.")
                continue
            
            # 确保所有单词都在词汇表中
            if any(w not in wv for w in words):
                missing_words_count += 1  # 增加未发现词数
                #print(f"{line} has word(s) not in given embedding: {words}")
                continue
            
            try:
                # 计算最相似的词
                result = wv.most_similar(positive=[words[1], words[2]], negative=[words[0]])
                rank, pred = find_idx_for_word(words[3], result)
                if rank is not None:
                    ranks.append(rank + 1)  # 排名从1开始计数
                right_pred += pred
                num += 1
            except Exception as e:
                pass
                #print(f"Error processing line {i}: {e}")
    
    # 处理最后一个类别
    if prev_topic and num > 0:
        res_dict[prev_topic] = {
            'count': num,
            'acc': right_pred / num,
            'average_ranks': np.nanmean(ranks) if ranks else float('nan'),
            'missing_words': missing_words_count
        }
        total_missing_words[prev_topic] = missing_words_count

    # 使用 PrettyTable 展示结果
    table = PrettyTable()
    table.field_names = ["Category", "发现词语", "未发现词语", "准确率 (%)", "平均排名"]
    
    for key, val in res_dict.items():
        table.add_row([
            key,
            val['count'],
            val['missing_words'],
            f"{val['acc'] * 100:.2f}",
            f"{val['average_ranks']:.2f}" if not np.isnan(val['average_ranks']) else "NaN"
        ])
    
    print("\n评估结果：")
    print(table)
    
    

    
    
    
def evaluate_similarity(wv, file=None):
    """
    评估词向量模型语义相似表现。 使用Spearman's Rank Coeficient作为评价指标， 取值[-1, 1], 1完全相关，-1完全负相关， 0毫无相关性。
    
    测试文件格式:
        词语1 词语2 相似度
        词语1 词语2 相似度
        ...
        词语1 词语2 相似度

    Args:
        wv (KeyedVectors): 词向量模型
        file (str): 测试文件路径，默认使用cntext内置的similarity.txt文件。
    """
    if file is None:
        file = Path(__file__).parent /  "evaluate_data" / "similarity.txt"
        name = Path(file).stem
        print(f"近义测试: {name}.txt")
        print(file)
    else:
        name = Path(file).stem
        print(f"近义测试: {name}.txt")
        
    pred, label, found = [], [], 0
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in tqdm(lines, desc="Processing Similarity Test"):
            w1, w2, score = line.split()
            if w1 in wv and w2 in wv:
                found += 1
                cosine_score = 1 - spatial.distance.cosine(wv[w1], wv[w2])
                pred.append(cosine_score)
                label.append(float(score))
    
    src = spearmanr(label, pred)[0]
    
    table = PrettyTable()
    print("\n评估结果：")
    table.field_names = ["发现词语", "未发现词语", "Spearman's Rank Coeficient"]
    table.add_row([found, len(lines) - found, f"{src:.2f}"])
    print(table)
    
      
    
    
def get_optimal_threshold():
    """根据系统总内存动态调整内存阈值"""
    total_mem = psutil.virtual_memory().total / (1024 ** 3)  # 获取总内存，单位GB
    used_mem = psutil.virtual_memory().used / (1024 ** 3)    # 获取已用内存
    if total_mem < 8:
        return 0.5  # 小内存系统
    elif total_mem < 16:
        return 0.6  # 中等内存系统
    elif total_mem < 32:
        return 0.7  # 大内存系统
    elif total_mem < 64:
        return 0.8  # 非常大内存系统
    else:
        # 对于超大内存系统，如果当前内存使用率低于50%，则使用0.85，否则使用0.75
        return 0.85 if (used_mem / total_mem) < 0.5 else 0.75
    


def load_userdict(dict_file=None):
    """
    加载用户自定义词典。

    Args:
        dict_file (str): 词典txt文件路径。每行一个词
    """
    if dict_file:
        jieba.load_userdict(dict_file)
        
    system = platform.system()
    
    if system == 'Windows':
        print('Windows System, Unable Parallel Processing')
    else:
        print('Mac(Linux) System, Enable Parallel Processing')
        jieba.enable_parallel(multiprocessing.cpu_count())
    


            
    












# ==============================
# 全局常量：内部使用
# ==============================
# 1. 空停用词集合
_EMPTY_STOPWORDS = frozenset()

# 2. 中文字符 + 英文字母 + 数字 + 空格 + 常见中文标点
_CHINESE_CHARS = r'\u4e00-\u9fff'
_ENGLISH_CHARS = r'a-zA-Z'
_DIGITS = r'0-9'
_PUNCTUATION = r'，。！？；：""''（）【】《》、·…—'
# 用于保留基本字符的模式
_KEEP_PATTERN = f'[^{_CHINESE_CHARS}{_ENGLISH_CHARS}{_DIGITS}\\s{_PUNCTUATION}]'

# 3. 数字归一化标记
_NUM_TOKEN = 'NUM'

# 4. 是否启用数字归一化
_REPLACE_NUMBERS = True

# 5. ✅ 新增：URL 正则表达式（支持 http/https/www 及常见域名）
# 这个正则可以匹配大多数常见的 URL 形式
_URL_PATTERN = re.compile(
    r'https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9][-a-zA-Z0-9]*\.(?:com|net|org|gov|cn|io|app|me|edu|mil)[/\w\d\.\?\=\&\%\#\-\_\~\:\@\+]*',
    re.IGNORECASE
)


# ==============================
# 核心函数：仅暴露 3 个接口
# ==============================
def preprocess_line(
    line: str,
    lang: str = 'chinese',
    stopwords: Optional[Set[str]] = None
) -> List[str]:
    """
    根据语言对单行文本进行预处理。
    自动剔除 URL、归一化数字、清洗噪声字符。

    Args:
        line (str): 输入的一行文本。
        lang (str): 语言类型，支持 'chinese' 或 'english'。
        stopwords (set, optional): 停用词集合。默认为 None（不过滤停用词）。

    Returns:
        list: 预处理后的分词结果。
    """
    # 去除首尾空白并检查空行
    line = line.strip()
    if not line:
        return []

    # 处理停用词
    stopwords_set = frozenset(stopwords) if stopwords else _EMPTY_STOPWORDS

    if lang == 'chinese':
        # 转小写（统一英文字母）
        cleaned_line = line.lower()

        # ✅ 步骤1: 移除 URL（在其他清洗之前）
        # 这样可以避免 URL 中的特殊字符干扰后续处理
        cleaned_line = _URL_PATTERN.sub('', cleaned_line)

        # 步骤2: 数字归一化
        if _REPLACE_NUMBERS:
            cleaned_line = re.sub(r'\d+\.?\d*', _NUM_TOKEN, cleaned_line)
        
        # 步骤3: 清除剩余噪声字符（只保留指定字符）
        cleaned_line = re.sub(_KEEP_PATTERN, '', cleaned_line)
        
        # 步骤4: 分词
        word_generator = (w.strip() for w in jieba.cut(cleaned_line))
        
        # 步骤5: 过滤
        tokens = [
            word for word in word_generator
            if word and word not in stopwords_set and len(word) > 1
        ]

    elif lang == 'english':
        cleaned_line = line.lower()
        cleaned_line = _URL_PATTERN.sub('', cleaned_line)  # ✅ 移除 URL
        
        if _REPLACE_NUMBERS:
            cleaned_line = re.sub(r'\d+\.?\d*', _NUM_TOKEN, cleaned_line)
        
        cleaned_line = re.sub(r'[^a-zA-Z0-9\s\.,;:!?]', '', cleaned_line)
        
        word_generator = (w.strip() for w in word_tokenize(cleaned_line))
        tokens = [
            word for word in word_generator
            if word and word not in stopwords_set
        ]
    else:
        raise ValueError(f"Unsupported language: {lang}")

    return tokens
    
    
    
#常见符号
punctuation = '＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､\u3000、〃〈〉《》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏﹑﹔·．！？｡。'

def preprocess_line(line, lang='chinese', stopwords=None):
    """
    根据语言对单行文本进行预处理。
    
    Args:
        line (str): 输入的一行文本。
        lang (str): 语言类型，支持 'chinese' 或 'english'。
        stopwords (set): 停用词集合。
        
    Returns:
        list: 预处理后的分词结果。
    """
    # 去除首尾空格并检查空行
    line = line.strip()
    if not line:
        return []
    
    # 将停用词转换为frozenset
    stopwords = frozenset(stopwords) if stopwords else frozenset()

    if lang == 'chinese':
        line = re.sub(f'[^{punctuation}\u4e00-\u9fa5a-zA-Z0-9]', '', line.lower())
        # 使用生成器表达式优化内存
        tokens = [word 
                  for word in (w.strip() for w in jieba.cut(line))
                  if word and word not in stopwords and len(word)>1]
    elif lang == 'english':
        # 使用生成器表达式优化内存
        line = re.sub(f'[^{punctuation}a-zA-Z0-9]', '', line.lower())
        tokens = [word for word in (w.strip() for w in word_tokenize(line))
                 if word and word not in stopwords]
    else:
        raise ValueError(f"Unsupported language: {lang}")

    return tokens

######################################################################################################################

def co_occurrence_matrix(documents, window_size=2, lang='chinese'):
    """_summary_
    构建共词矩阵

    Args:
        documents (list): 文档列表
        window_size (int, optional):  共现范围. 默认2.
        lang (str, optional): 支持中英文，默认'chinese'.

    Returns:
        dict
    """
    d = defaultdict(int)
    vocab = set()
    if lang == 'english':
        for document in documents:
            document = document.lower().split()
            for i in range(len(document)):
                token = document[i]
                vocab.add(token)  # add to vocab
                next_token = document[i + 1: i + 1 + window_size]
                for t in next_token:
                    key = tuple(sorted([t, token]))
                    d[key] += 1

    elif lang =='chinese':
        for document in documents:
            document = list(jieba.cut(document))
            # iterate over sentences
            for i in range(len(list(document))):
                token = document[i]
                vocab.add(token)  # add to vocab
                next_token = document[i + 1: i + 1 + window_size]
                for t in next_token:
                    key = tuple(sorted([t, token]))
                    d[key] += 1
                    
    # formulate the dictionary into dataframe
    vocab = sorted(vocab)  # sort vocab
    df = pd.DataFrame(data=np.zeros((len(vocab), len(vocab)), dtype=np.int16),
                      index=vocab,
                      columns=vocab)
    for key, value in d.items():
        df.at[key[0], key[1]] = value
        df.at[key[1], key[0]] = value
    return df


######################################################################################   
        

def expand_dictionary(wv, seeddict, topn=100):
    """
    扩展词典, 结果保存到output文件夹内
    
    Args:
        wv (Word2VecKeyedVectors): 预训练模型，数据类型为 gensim.models.keyedvectors.KeyedVectors。
        seeddict (dict): 参数类似于种子词；格式为PYTHON字典；
                         examples seeddict = {'pos': ['happy', 'wonderful', 'good'],
                                              'neg': ['bad', 'ugly', 'terrible'}
        topn (int, optional): 返回topn个语义最接近seeddict的词，默认100.

    
    Returns:
    """
    resultdict = dict()
    for seed_name in seeddict.keys():
        seedwords = seeddict[seed_name]
        simidx_scores = []
        similars_candidate_idxs = [] #the candidate words of seedwords
        dictionary = wv.key_to_index
        seedidxs = [] #transform word to index
        for seed in seedwords:
            if seed in dictionary:
                seedidx = dictionary[seed]
                seedidxs.append(seedidx)
        for seedidx in seedidxs:
            # sims_words such as [('by', 0.99984), ('or', 0.99982), ('an', 0.99981), ('up', 0.99980)]
            sims_words = wv.similar_by_word(seedidx, topn=topn)
            #Convert words to index and store them
            similars_candidate_idxs.extend([dictionary[sim[0]] for sim in sims_words])
        similars_candidate_idxs = set(similars_candidate_idxs)
        
        for idx in similars_candidate_idxs:
            score = wv.n_similarity([idx], seedidxs)
            simidx_scores.append((idx, score))
        simidxs = [w[0] for w in sorted(simidx_scores, key=lambda k:k[1], reverse=True)]

        simwords = [str(wv.index_to_key[idx]) for idx in simidxs][:topn]

        resultwords = []
        resultwords.extend(seedwords)
        resultwords.extend(simwords)
        
        resultdict[seed_name] = resultwords
        
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        candidate_txt_file = output_dir / f'{seed_name}.txt'
            
        with open(candidate_txt_file, 'w', encoding='utf-8') as f:
            for word in resultwords:
                f.write(word+'\n')

        print(f'Finish! {seed_name} candidates saved to output/{seed_name}.txt')



######################################################################################   
        

from gensim.models import FastText

def load_w2v(w2v_path):
    """
    读取word2vec模型文件; 支持.bin、 .txt、 .vec格式。

    Args:
        wv_path (str): word2vec模型文件路径

    Returns: gensim.models.keyedvectors.KeyedVectors
    """
    if w2v_path.endswith('.bin'):
        binary = True
        if '-FastText.' in w2v_path:
            model = FastText.load(w2v_path)
            wv = model.wv
        else:
            wv = KeyedVectors.load_word2vec_format(w2v_path, binary=binary)
            
    else:
        wv = KeyedVectors.load_word2vec_format(w2v_path, binary=False)
       
    
    print(f'Loading {w2v_path}...')
    return wv




######################################################################################   
        

def glove2word2vec(glove_file, word2vec_file):
    """
    将glove模型转换为word2vec模型。
    Args:
        glove_file (str): glove模型.txt文件路径
        word2vec_file (str): word2vec模型.txt文件路径
        
    Returns: 
        gensim.models.keyedvectors.KeyedVectors
    """
    # 使用 glove2word2vec 转换格式
    print('Converting GloVe model to Word2Vec format...')
    glove2wv(glove_file, word2vec_file)
    print('Finish! The word2vec model has been saved to {}.'.format(word2vec_file))
    glove_model = KeyedVectors.load_word2vec_format(word2vec_file, binary=False)
    return glove_model


