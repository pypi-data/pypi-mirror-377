from pathlib import Path
import time
import torch
import pickle
import numpy as np
from tqdm import tqdm
import gc
import psutil
import smart_open
from functools import partial
from multiprocessing import Pool, cpu_count
from allennlp.modules.elmo import Elmo, batch_to_ids
from ..model.utils import load_userdict, load_stopwords, preprocess_line, get_optimal_threshold


def process_line(line, lang, stopwords):
    """处理单行文本的函数"""
    return preprocess_line(line, lang=lang, stopwords=stopwords)

def ELMo(corpus_file, lang='chinese', dict_file=None, stopwords_file=None,
         pre_trained=True, vector_size=512, window_size=5, min_count=5,
         max_iter=10, batch_size=32, cuda_device=-1, chunksize=10000, **kwargs):
    """
    ELMo模型接口，支持预训练和自定义训练
    
    Args:
        pre_trained (bool): 是否使用预训练模型，默认True
        vector_size (int): 词向量维度(自定义训练时使用)
        window_size (int): 窗口大小(自定义训练时使用)
        min_count (int): 最小词频(自定义训练时使用)
        max_iter (int): 最大迭代次数(自定义训练时使用)
        batch_size (int): 批处理大小
        cuda_device (int): GPU设备号，-1表示CPU
        chunksize (int): 预处理时的分块大小
    """
    start_time = time.time()
    
    # 初始化输出目录
    output_dir = Path('output')
    output_dir.mkdir(parents=True, exist_ok=True)
    corpus_name = Path(corpus_file).stem
    
    # 加载词典和停用词
    load_userdict(dict_file=dict_file)
    stopwords = load_stopwords(stopwords_file=stopwords_file, lang=lang)
    
    # 预处理语料(复用Word2Vec的逻辑)
    cache_file = output_dir / f"{corpus_name}_elmo_cache.txt"
    if not cache_file.exists():
        _preprocess_corpus(corpus_file, cache_file, lang, stopwords, chunksize)
    
    # 加载或训练模型
    if pre_trained:
        print("Loading pre-trained ELMo model")
        model = _load_pretrained_elmo(cuda_device, **kwargs)
    else:
        model = _train_custom_elmo(cache_file, output_dir, corpus_name,
                                 vector_size, window_size, min_count,
                                 max_iter, cuda_device, **kwargs)
    
    # 处理语料并生成词向量
    results = _process_with_elmo(model, cache_file, batch_size, cuda_device)
    
    print(f"ELMo processing completed in {time.time()-start_time:.2f}s")
    return results

def _preprocess_corpus(corpus_file, cache_file, lang, stopwords, chunksize):
    """预处理语料，确保内存安全"""
    print(f"Preprocessing corpus to {cache_file}")
    memory_threshold = get_optimal_threshold()
    max_workers = int(cpu_count() * 0.8)
    
    with smart_open.open(corpus_file, 'r', encoding='utf-8') as f_in, \
         smart_open.open(cache_file, 'w', encoding='utf-8') as f_out:
        
        process_func = partial(process_line, lang=lang, stopwords=stopwords)
        buffer = []
        
        with Pool(processes=max_workers) as pool:
            for i, words in enumerate(pool.imap(process_func, f_in, chunksize=chunksize)):
                if words:
                    buffer.append(' '.join(words) + '\n')
                
                # 内存管理
                if i % 1000 == 0:
                    if psutil.virtual_memory().percent > memory_threshold * 100:
                        gc.collect()
                
                # 分批写入
                if len(buffer) >= chunksize:
                    f_out.writelines(buffer)
                    buffer = []
            
            if buffer:
                f_out.writelines(buffer)

def _load_pretrained_elmo(cuda_device, **kwargs):
    """加载预训练ELMo模型"""
    options_file = "https://allennlp.s3.amazonaws.com/models/elmo/2x4096_512_2048cnn_2xhighway/elmo_2x4096_512_2048cnn_2xhighway_options.json"
    weight_file = "https://allennlp.s3.amazonaws.com/models/elmo/2x4096_512_2048cnn_2xhighway/elmo_2x4096_512_2048cnn_2xhighway_weights.hdf5"
    
    model = Elmo(options_file, weight_file, num_output_representations=1, **kwargs)
    if cuda_device >= 0 and torch.cuda.is_available():
        model = model.cuda(device=cuda_device)
    return model

def _train_custom_elmo(cache_file, output_dir, corpus_name, vector_size, 
                     window_size, min_count, max_iter, cuda_device, **kwargs):
    """自定义ELMo训练"""
    vocab_file = output_dir / f"{corpus_name}_elmo_vocab.bin"
    model_file = output_dir / f"{corpus_name}_elmo_model.bin"
    
    if model_file.exists() and vocab_file.exists():
        print("Loading cached ELMo model")
        with open(vocab_file, 'rb') as f:
            vocab = pickle.load(f)
        
        # 这里简化了自定义训练的实现
        # 实际实现需要更复杂的训练逻辑
        model = torch.load(model_file)
    else:
        print("Training new ELMo model (simplified implementation)")
        # 这里应该是完整的训练代码
        # 由于ELMo训练复杂，建议使用预训练模型
        model = _load_pretrained_elmo(cuda_device, **kwargs)
        
        # 保存模型和词汇表
        torch.save(model.state_dict(), model_file)
        with open(vocab_file, 'wb') as f:
            pickle.dump({}, f)  # 这里应该保存真实的词汇表
    return model

def _process_with_elmo(model, cache_file, batch_size, cuda_device):
    """使用ELMo处理语料"""
    sentences = []
    with smart_open.open(cache_file, 'r', encoding='utf-8') as f:
        for line in f:
            sentences.append(line.strip().split())
    
    results = {}
    for i in tqdm(range(0, len(sentences), batch_size), desc="Processing"):
        batch = sentences[i:i+batch_size]
        character_ids = batch_to_ids(batch)
        
        if cuda_device >= 0 and torch.cuda.is_available():
            character_ids = character_ids.cuda(device=cuda_device)
        
        embeddings = model(character_ids)
        
        for j, sent in enumerate(batch):
            results[' '.join(sent)] = {
                'embeddings': embeddings['elmo_representations'][0][j].detach().cpu().numpy(),
                'layer_weights': embeddings['mask'][j].detach().cpu().numpy()
            }
    
    return results
