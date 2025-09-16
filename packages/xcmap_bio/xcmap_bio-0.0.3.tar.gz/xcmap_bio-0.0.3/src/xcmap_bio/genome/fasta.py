from pyfaidx import Fasta
from typing import Iterator, Tuple


class FastaOptions:
    """
    高效 FASTA 读取工具类，基于 pyfaidx。
    支持随机访问区间、获取序列长度、遍历序列。
    """
    def __init__(self, fasta_path: str, rebuild_index: bool = False):
        self.handler = Fasta(fasta_path, rebuild=rebuild_index)

    def fetch_seq(self, seq_id: str, start: int = None, end: int = None):
        fasta_reader = _FastaReader(self.handler)
        return fasta_reader.get_seq(seq_id, start, end)


class _FastaReader:
    """
    高效 FASTA 工具类，基于 pyfaidx。
    支持随机访问区间、获取序列长度、遍历序列。
    """

    def __init__(self, handler):
        self.handler = handler

    def get_seq(self, seq_id: str, start: int = None, end: int = None) -> str:
        """
        获取序列区间 [start, end)，0-based 左闭右开。
        如果 start/end 都为空，返回整条序列。
        """
        seq = self.handler[seq_id]
        if start is None and end is None:
            return str(seq)
        return str(seq[start:end])

    def get_length(self, seq_id: str) -> int:
        """获取序列长度"""
        return len(self.handler[seq_id])

    def list_seq_ids(self):
        """返回所有序列 ID"""
        return list(self.handler.keys())

    def __iter__(self) -> Iterator[Tuple[str, str]]:
        """遍历所有序列 (seq_id, sequence)"""
        for seq_id in self.handler.keys():
            yield seq_id, str(self.handler[seq_id])

    def close(self):
        """关闭文件句柄"""
        self.handler.close()
