import chardet
import pkg_resources
from opencc import OpenCC
import ftfy
import contractions



def traditional2simple(text, mode='t2s'):
    """
    中文繁体 转 中文简体； 

    Args:
        text (str): 待转换的文本内容
        mode(str): 转换模式， 默认mode='t2s'繁转简; mode还支持s2t

    Returns:
        str: 返回转换成功的文本
    """
    
    cc = OpenCC(mode)  # 繁体2简体
    return cc.convert(text)





def get_cntext_path():
    """
    查看cntext的安装路径
    """
    return pkg_resources.resource_filename('cntext', '')







def detect_encoding(file, num_lines=100):
    """
    诊断某文件的编码方式

    Args:
        file (str): 文件路径
        num_lines (int, optional):  默认读取文件前100行.

    Returns:
        encoding type
    """
    try:
        import cchardet as chardet
        with open(file, "rb") as f:
            msg = f.read()
            result = chardet.detect(msg)
            return result['encoding']
    except:
        detector = chardet.UniversalDetector()
        with open(file, 'rb') as f:
            for line in f:
                detector.feed(line)
                if detector.done:
                    break
                num_lines -= 1
                if num_lines == 0:
                    break
        detector.close()
        return detector.result['encoding']






def fix_text(text):
    """
    将不正常的、混乱编码的文本转化为正常的文本。
    :param text:
    :return:
    """
    return ftfy.fix_text(text)



def fix_contractions(text):
    """
    英文缩写处理函数， 如you're -> you are
    
    Args:
        text (str): 待分句的中文文本
        
    Returns:
        text(str)
    """
    return contractions.fix(text)



