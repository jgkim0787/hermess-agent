# hermes/rag.py
"""Hermes의 지식 검색(RAG) backend — 로컬 문서를 TF-IDF로 embedding해 cosine 유사도로 검색한다.

★ Anthropic에는 임베딩(embeddings) API가 없다 — claude-api-cheatsheet에도 없다.
   그래서 embedding을 순수 파이썬 TF-IDF(어휘 기반 스파스 벡터)로 '직접' 만든다.
   이건 버그가 아니라 설계다: 파이프라인(chunk → embed → cosine top-k → 주입 → 생성)은
   프로덕션 RAG와 100% 동일하고, 프로덕션과 다른 seam은 embed(text) -> vector 함수 딱 한 곳이다
   (어휘(lexical) 유사도 → 신경망 의미(semantic) 유사도). numpy·vector DB 없이 표준 라이브러리만.
"""
import math
import os
import glob
import re
from collections import Counter

from .config import KB_DIR, TOP_K   # rag는 config만 import한다(llm 불필요 — 임베딩에 Claude를 안 쓴다)


def tokenize(text: str) -> list:
    """소문자화 + 한글/영문/숫자 단어만 추출. query와 chunk가 '같은 규칙'으로 쪼개져야
    같은 벡터 공간에 놓인다 — 그래서 이 함수 하나를 양쪽에서 공용한다."""
    return re.findall(r"[가-힣a-zA-Z0-9_]+", text.lower())


def chunk_text(text: str, max_chars: int = 500) -> list:
    """문서를 검색·임베딩의 단위인 chunk로 쪼갠다. 문단(빈 줄) 기준으로 나누고,
    한 문단이 너무 길면 max_chars로 잘라 여러 chunk로 만든다.
    (chunk가 너무 크면 유사도가 희석되고, 너무 작으면 맥락이 끊긴다 — 여기선 단순한 문단 방식.)"""
    chunks = []
    for para in re.split(r"\n\s*\n", text):     # 빈 줄로 문단 분리
        para = para.strip()
        if not para:
            continue
        if len(para) <= max_chars:
            chunks.append(para)
        else:                                    # 너무 길면 고정 길이로 더 자른다
            for i in range(0, len(para), max_chars):
                chunks.append(para[i:i + max_chars])
    return chunks


def compute_idf(chunk_token_lists: list) -> dict:
    """코퍼스 전체의 IDF(역문서빈도)를 계산한다. ★ smoothed 공식:
        idf(t) = log((N+1) / (df(t)+1)) + 1
    ⚠ 평범한 log(N/df)는 '모든 chunk에 있는 단어'의 idf를 0으로 만들어(→ 벡터가 죽는다),
       문서 수가 적은 작은 코퍼스에서 특히 위험하다. +1 smoothing이 그걸 막는다."""
    N = len(chunk_token_lists)
    df = Counter()
    for tokens in chunk_token_lists:
        for t in set(tokens):                    # 한 chunk에서 같은 단어는 한 번만(document frequency)
            df[t] += 1
    return {t: math.log((N + 1) / (df_t + 1)) + 1 for t, df_t in df.items()}


def tfidf_vector(tokens: list, idf: dict) -> dict:
    """★ 우리의 embedding — 토큰 리스트를 {단어: TF-IDF 가중치} 스파스 벡터(dict)로 만든다.
    query도 반드시 '코퍼스에서 만든 같은 idf'로 벡터화해야 같은 공간에 놓인다."""
    tf = Counter(tokens)
    n = len(tokens) or 1                          # 빈 입력의 0으로 나누기 방지
    return {t: tf[t] / n * idf.get(t, 0.0) for t in tf}


def cosine(a: dict, b: dict) -> float:
    """두 스파스 벡터(dict)의 코사인 유사도. 방향(각도)만 보므로 문서 길이에 안 휘둘린다."""
    dot = sum(w * b.get(t, 0.0) for t, w in a.items())
    na = math.sqrt(sum(w * w for w in a.values()))
    nb = math.sqrt(sum(w * w for w in b.values()))
    return dot / (na * nb) if na and nb else 0.0  # ★ 0-norm 가드: 겹치는 단어 0이면 ZeroDivisionError


class DocIndex:
    """색인(상태)을 소유하는 클래스 — M4의 class Memory와 같은 계보다.
    build로 폴더를 읽어 chunk 벡터들과 idf를 들고 있고, search로 질의에 답한다."""

    def __init__(self):
        self.chunks = []      # chunk 원문(list[str]) — 검색 결과로 이걸 돌려준다
        self.vectors = []     # 각 chunk의 embedding(list[dict]) — chunks와 같은 순서
        self.idf = {}         # 코퍼스 idf — query 벡터화에도 '같은' 걸 쓴다

    def build(self, folder: str) -> "DocIndex":
        """folder의 .md 파일들을 읽어 chunk → idf → chunk 벡터로 색인한다."""
        self.chunks = []
        for path in sorted(glob.glob(os.path.join(folder, "*.md"))):
            with open(path, "r", encoding="utf-8") as f:
                self.chunks.extend(chunk_text(f.read()))
        token_lists = [tokenize(c) for c in self.chunks]
        self.idf = compute_idf(token_lists)
        self.vectors = [tfidf_vector(toks, self.idf) for toks in token_lists]
        return self           # build().search() 로 이어 쓸 수 있게 self 반환

    def search(self, query: str, k: int = TOP_K) -> list:
        """★ retrieval의 실체 — query를 '같은 idf'로 벡터화해 각 chunk와 cosine을 재고,
        높은 순으로 상위 k개 chunk 텍스트를 반환한다(점수 0=전혀 안 겹침은 버린다)."""
        qv = tfidf_vector(tokenize(query), self.idf)
        scored = [(cosine(qv, v), c) for v, c in zip(self.vectors, self.chunks)]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [c for score, c in scored[:k] if score > 0]


# 모듈 레벨 게으른 싱글턴 — import 시점이 아니라 '첫 검색 때' 파일을 읽어 색인한다.
_INDEX = None


def search(query: str, k: int = TOP_K) -> list:
    """tools.py가 부르는 검색 진입점. 처음 불릴 때 KB_DIR을 색인하고, 이후엔 재사용한다."""
    global _INDEX
    if _INDEX is None:
        _INDEX = DocIndex().build(KB_DIR)
    return _INDEX.search(query, k)
