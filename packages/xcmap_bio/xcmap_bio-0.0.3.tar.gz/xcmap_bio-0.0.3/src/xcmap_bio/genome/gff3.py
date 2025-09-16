import time
from functools import lru_cache
from typing import Optional, Union, List, Tuple

import pandas as pd
from pydantic import BaseModel


class Gff3ColumnName:
    """
    序列 ID（染色体、contig 等），必须与参考序列一致, 如chr1
    """
    SEQ_ID = "seq_id"
    """
    特征来源（预测程序、数据库名等）如Ensembl
    """
    SOURCE = "source"
    """
    特征类型（使用 SO ontology term）, 如gene, mRNA, exon, CDS
    """
    TYPE = "type"
    """
    起始位置（1-based, inclusive）
    """
    START = "start"
    """
    结束位置（1-based, inclusive）
    """
    END = "end"
    """
    打分值（浮点数，或 . 代表无值）
    """
    SCORE = "score"
    """
    链信息（+, -, 或 . 未知）
    """
    STRAND = "strand"
    """
    仅对 CDS 有意义，取值为 0, 1, 2（表示阅读框相对起点偏移），其他特征用 .
    """
    PHASE = "phase"
    """
    属性字段，key=value 对形式，以 ; 分隔；至少应包含 ID 或 Parent, 如ID=mRNA0001;Parent=gene0001;Name=BRCA1-201
    """
    ATTRIBUTES = "attributes"


    @classmethod
    def fetch_values(cls):
        return [
            value
            for name, value in vars(cls).items()
            if not name.startswith('_') and not callable(value) and name != 'fetch_values'
        ]

class Gff3Options:
    _df_registry = {}

    """
    GFF3 file parser
    """
    def __init__(self, gff3_path):
        self.gff3_path = gff3_path
        self.df = self.read_gff3(gff3_path)
        # 注册 DataFrame
        self._df_registry[id(self.df)] = self.df

    class PageRequest(BaseModel):
        """
        分页查询请求，like query = GFF3Query(df)
            result, total = (
            query.filter(seqid=["chr1", "chr2"], feature_type=["gene", "exon"], start=200, end=400)
            .order(order_by=["seqid", "start"], ascending=[True, False])
            .paginate(page=1, page_size=2)
        )
        """
        seq_id: Optional[Union[str, List[str], None]] = None
        type: Optional[Union[str, List[str], None]] = None
        start: Optional[int] =  None
        end: Optional[int] =  None
        order_by: Optional[Union[str, List[str]]] = Gff3ColumnName.START
        ascending: Optional[Union[bool, List[bool]]] = True
        page: int = 1
        size: int = 20


    @staticmethod
    @lru_cache
    def read_gff3(gff3_path):
        df =  pd.read_csv(gff3_path,
                           skiprows=1,
                           header=None,
                           sep="\t",
                           names=Gff3ColumnName.fetch_values()
                           )
        def extract_attr(attrs, key):
            for item in attrs.split(";"):
                if item.startswith(f"{key}="):
                    return item.split("=", 1)[1]
            return None
        df["ID"] = df[Gff3ColumnName.ATTRIBUTES].apply(lambda x: extract_attr(x, "ID"))
        df["Parent"] = df[Gff3ColumnName.ATTRIBUTES].apply(lambda x: extract_attr(x, "Parent"))
        return df

    def fetch_page(self, page_request: PageRequest) -> Tuple[List[dict], int]:
        """
        分页查询gff3数据
        :param page_request:
        :return:
        """
        return _GFF3Query(self.df).filter(
            seq_id=page_request.seq_id,
            seq_type=page_request.type,
            start=page_request.start,
            end=page_request.end
        ).order(
            order_by=page_request.order_by,
            ascending=page_request.ascending
        ).paginate(
            page=page_request.page,
            size=page_request.size
        )

    def fetch_by_gene_id(self, gene_id, is_contain_descendants=True):
        children_df = self._find_children(id(self.df), parent_id=gene_id)
        if children_df.empty:
            return []
        results = []
        if is_contain_descendants:
            for children_dict in children_df.to_dict(orient="records"):
                if not children_dict.get("ID"):
                    continue
                descendants_df = self._find_descendants(id(self.df), parent_id=children_dict.get("ID"))
                if descendants_df.empty:
                    continue
                children_dict["feature_list"] = descendants_df.to_dict(orient="records")
                results.append(children_dict)
        else:
            results = children_df.to_dict(orient="records")
        return results

    @staticmethod
    @lru_cache
    def _find_children(df_id: int,
                       parent_id: str,
                       seq_id: Optional[str] = None,
                       feature_type: Optional[str] = None) -> pd.DataFrame:
        """查找直接子节点（跨实例缓存，依赖 df 的 id 和 parent_id）"""
        df = Gff3Options._df_registry[df_id]  # 从全局字典取 df
        result = df[df["Parent"] == parent_id]
        if seq_id:
            result = result[result["seq_id"] == seq_id]
        if feature_type:
            result = result[result["type"] == feature_type]
        return result

    @staticmethod
    @lru_cache
    def _find_descendants(df_id: int,
                          parent_id: str,
                          seq_id: Optional[str] = None,
                          feature_type: Optional[str] = None) -> pd.DataFrame:
        """查找所有后代（逐层展开，不做递归遍历），跨实例缓存"""
        df = Gff3Options._df_registry[df_id]
        results = []
        to_visit = [parent_id]
        while to_visit:
            children = df[df["Parent"].isin(to_visit)]
            if children.empty:
                break
            results.append(children)
            to_visit = [x for x in children["ID"].tolist() if x is not None]

        if results:
            result = pd.concat(results, ignore_index=True)
            if seq_id:
                result = result[result["seq_id"] == seq_id]
            if feature_type:
                result = result[result["type"] == feature_type]
            return result
        else:
            return pd.DataFrame(columns=df.columns)

class _GFF3Query:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.filtered = self.df

    def filter(
        self,
        seq_id: Union[str, List[str], None] = None,
        seq_type: Union[str, List[str], None] = None,
        start: int = None,
        end: int = None,
    ):
        """条件过滤"""
        if seq_id is not None:
            if isinstance(seq_id, list):
                self.filtered = self.filtered[self.filtered[Gff3ColumnName.SEQ_ID].isin(seq_id)]
            else:
                self.filtered = self.filtered[self.filtered[Gff3ColumnName.SEQ_ID] == seq_id]

        if seq_type is not None:
            if isinstance(seq_type, list):
                self.filtered = self.filtered[self.filtered[Gff3ColumnName.TYPE].isin(seq_type)]
            else:
                self.filtered = self.filtered[self.filtered[Gff3ColumnName.TYPE] == seq_type]

        if start is not None:
            self.filtered = self.filtered[self.filtered[Gff3ColumnName.START] >= start]
        if end is not None:
            self.filtered = self.filtered[self.filtered[Gff3ColumnName.END] <= end]

        return self

    def order(self, order_by: Union[str, List[str]] = Gff3ColumnName.START, ascending: Union[bool, List[bool]] = True):
        """排序，可支持多字段"""
        if isinstance(order_by, str):
            order_by = [order_by]
        if isinstance(ascending, bool):
            ascending = [ascending] * len(order_by)

        valid_cols = [col for col in order_by if col in self.filtered.columns]
        if valid_cols:
            self.filtered = self.filtered.sort_values(by=valid_cols, ascending=ascending)

        return self

    def paginate(self, page: int = 1, size: int = 20) -> Tuple[List[dict], int]:
        """分页，并返回 (结果list, 总条数)"""
        total_count = len(self.filtered)
        offset = (page - 1) * size
        page_df = self.filtered.iloc[offset: offset + size]
        return page_df.to_dict(orient="records"), total_count


# if __name__ == '__main__':
#     gff3_options = Gff3Options("/Users/zhangyang/Downloads/_omdb_data/genome/EVM.final.gene.gff3")
#     result = gff3_options.fetch_by_gene_id('EVM0011117', is_contain_descendants=True)
#     print(result)
#     time.sleep(20)
#     gff3_options = Gff3Options("/Users/zhangyang/Downloads/_omdb_data/genome/EVM.final.gene.gff3")
#     result = gff3_options.fetch_by_gene_id('EVM0011117', is_contain_descendants=True)
#     print(result)