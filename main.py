from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime

app = FastAPI()

# --- CORS 설정 (Netlify + 기타 전부 허용) ---
origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "https://upsourcing-tool.netlify.app",
    "*",  # 귀찮으니까 일단 전부 허용
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- 데이터 모델 ----------

class CollectRequest(BaseModel):
    keyword: str
    min_price: int
    max_price: int


class Mall(BaseModel):
    id: int
    name: str
    link: str
    logo: str | None = None
    collected_at: datetime


# 메모리 안에서만 쓰는 임시 DB
malls_db: List[Mall] = []


# ---------- 헬스체크 ----------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "time": datetime.utcnow().isoformat(),
    }


# ---------- BEST 소싱 수집 (POST) ----------

@app.post("/api/collect/best")
def collect_best(req: CollectRequest):
    """
    스마트스토어 BEST 수집 (테스트용 더미 데이터)
    실제 크롤링 대신, keyword 섞어서 가짜 쇼핑몰 5개 만들어 저장
    """
    global malls_db
    malls_db = []  # 요청 올 때마다 초기화

    base_link = "https://smartstore.naver.com"

    dummy_raw = [
        {
            "id": 1,
            "name": f"{req.keyword} 감성 여성의류샵",
            "link": f"{base_link}/example1",
            "logo": "https://via.placeholder.com/64?text=SHOP1",
        },
        {
            "id": 2,
            "name": f"{req.keyword} 니트 전문몰",
            "link": f"{base_link}/example2",
            "logo": "https://via.placeholder.com/64?text=SHOP2",
        },
        {
            "id": 3,
            "name": f"{req.keyword} 해외직구 편집샵",
            "link": f"{base_link}/example3",
            "logo": "https://via.placeholder.com/64?text=SHOP3",
        },
        {
            "id": 4,
            "name": f"{req.keyword} 데일리룩 쇼핑몰",
            "link": f"{base_link}/example4",
            "logo": "https://via.placeholder.com/64?text=SHOP4",
        },
        {
            "id": 5,
            "name": f"{req.keyword} 하이브랜드 셀렉샵",
            "link": f"{base_link}/example5",
            "logo": "https://via.placeholder.com/64?text=SHOP5",
        },
    ]

    now = datetime.utcnow()
    malls_db = [
        Mall(
            id=item["id"],
            name=item["name"],
            link=item["link"],
            logo=item["logo"],
            collected_at=now,
        )
        for item in dummy_raw
    ]

    return {
        "ok": True,
        "count": len(malls_db),
        "keyword": req.keyword,
        "collected_at": now.isoformat(),
    }


# ---------- BEST 소싱 수집 (GET 버전) ----------
# 혹시 프론트에서 GET으로 호출해도 되게 둘 다 열어둠

@app.get("/api/collect/best")
def collect_best_get(
    keyword: str,
    min_price: int = 0,
    max_price: int = 999999999,
):
    req = CollectRequest(keyword=keyword, min_price=min_price, max_price=max_price)
    return collect_best(req)


# ---------- 수집된 쇼핑몰 목록 ----------

@app.get("/api/malls", response_model=List[Mall])
def list_malls():
    return malls_db


# ---------- 수집된 쇼핑몰 전체 삭제 ----------

@app.delete("/api/malls")
def clear_malls():
    malls_db.clear()
    return {"ok": True, "message": "모든 쇼핑몰이 삭제되었습니다."}