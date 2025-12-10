from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

app = FastAPI()

# CORS: 프론트 도메인 포함해서 모두 허용 (개발 편하게)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------
# 데이터 모델
# -----------------------------------
class Mall(BaseModel):
    id: int
    name: str
    keyword: Optional[str] = None
    logo_url: Optional[str] = None
    last_collected_at: Optional[datetime] = None


class CollectRequest(BaseModel):
    keyword: str
    min_price: Optional[int] = None
    max_price: Optional[int] = None


# 메모리 안에만 임시 저장 (DB 대신)
malls_db: List[Mall] = []
next_id: int = 1


# -----------------------------------
# 쇼핑몰 목록 조회
# GET /api/malls
# -----------------------------------
@app.get("/api/malls")
def list_malls(sort_by: str = "recent", keyword: str = "") -> List[Mall]:
    """
    sort_by: recent, name, oldest
    keyword: 이름/키워드에 포함되는 문자열
    """
    # 키워드 필터
    if keyword:
        k = keyword.lower()
        filtered = [
            m
            for m in malls_db
            if k in m.name.lower() or (m.keyword and k in m.keyword.lower())
        ]
    else:
        filtered = list(malls_db)

    # 정렬
    if sort_by == "name":
        filtered.sort(key=lambda m: m.name)
    elif sort_by == "oldest":
        filtered.sort(
            key=lambda m: m.last_collected_at or datetime.fromtimestamp(0)
        )
    else:  # recent (최신 순)
        filtered.sort(
            key=lambda m: m.last_collected_at or datetime.fromtimestamp(0),
            reverse=True,
        )

    return filtered


# -----------------------------------
# BEST 소싱 (더미 수집)
# POST /api/smartstore/collect
# -----------------------------------
@app.post("/api/smartstore/collect")
def collect_smartstore(req: CollectRequest):
    """
    실제 크롤링 대신,
    keyword 기준으로 더미 쇼핑몰 3개를 생성해서 malls_db 에 추가.
    """
    global next_id, malls_db

    now = datetime.utcnow()

    dummy_names = [
        f"{req.keyword} 스토어 1",
        f"{req.keyword} 스토어 2",
        f"{req.keyword} 스토어 3",
    ]

    for name in dummy_names:
        mall = Mall(
            id=next_id,
            name=name,
            keyword=req.keyword,
            logo_url=None,
            last_collected_at=now,
        )
        malls_db.append(mall)
        next_id += 1

    return {
        "detail": "ok",
        "added": len(dummy_names),
        "keyword": req.keyword,
    }


# -----------------------------------
# 전체 쇼핑몰 삭제
# DELETE /api/malls
# -----------------------------------
@app.delete("/api/malls")
def clear_malls():
    global malls_db
    malls_db = []
    return {"detail": "cleared"}