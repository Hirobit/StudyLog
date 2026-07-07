from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, get_db
from pydantic import BaseModel
import models
from auth import verify_google_id_token, create_access_token, decode_access_token

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://studylog-03pu.onrender.com"],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)

# スキーマ定義
class CategoryCreate(BaseModel):
    name: str

class CategoryResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class SubcategoryCreate(BaseModel):
    name: str
    category_id: int

class SubcategoryResponse(BaseModel):
    id: int
    name: str
    category_id: int

    class Config:
        from_attributes = True

# ログイン用スキーマ
class GoogleLoginRequest(BaseModel):
    id_token: str

class UserResponse(BaseModel):
    id: str
    name: str | None

    class Config:
        from_attributes = True

def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> models.User:
    """
    リクエストヘッダーの Authorization: Bearer <JWT> を検証し、
    対応するユーザーをDBから取得して返す。
    トークンが無い/不正/期限切れ、またはユーザーが存在しない場合は401を返す。
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.replace("Bearer ", "")
    try:
        user_id = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# Googleログイン
@app.post("/auth/google")
def google_login(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    try:
        user_info = verify_google_id_token(payload.id_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    user = db.query(models.User).filter(models.User.google_id == user_info["google_id"]).first()
    if not user:
        user = models.User(
            google_id=user_info["google_id"],
            name=user_info["name"],
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(user.id)
    return {"access_token": access_token, "token_type": "bearer"}


# ログイン中ユーザー情報取得
@app.get("/auth/me", response_model=UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# カテゴリ一覧取得
@app.get("/categories")
def get_categories(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Category).filter(models.Category.user_id == current_user.id).all()

# カテゴリ作成
@app.post("/categories", response_model=CategoryResponse)
def create_category(category: CategoryCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_category = models.Category(name=category.name, user_id=current_user.id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# カテゴリ編集
@app.put("/categories/{id}", response_model=CategoryResponse)
def update_category(id: int, category: CategoryCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_category = db.query(models.Category).filter(
        models.Category.id == id,
        models.Category.user_id == current_user.id
    ).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    db_category.name = category.name
    db.commit()
    db.refresh(db_category)
    return db_category

# カテゴリ削除
@app.delete("/categories/{id}")
def delete_category(id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_category = db.query(models.Category).filter(
        models.Category.id == id,
        models.Category.user_id == current_user.id
    ).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(db_category)
    db.commit()
    return {"message": "Deleted"}

# サブカテゴリ一覧取得
@app.get("/subcategories/{category_id}")
def get_subcategories(category_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Subcategory).filter(
        models.Subcategory.category_id == category_id,
        models.Subcategory.user_id == current_user.id
    ).all()

# サブカテゴリ作成
@app.post("/subcategories", response_model=SubcategoryResponse)
def create_subcategory(subcategory: SubcategoryCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    parent_category = db.query(models.Category).filter(
        models.Category.id == subcategory.category_id,
        models.Category.user_id == current_user.id
    ).first()
    if not parent_category:
        raise HTTPException(status_code=404, detail="Category not found")

    db_sub = models.Subcategory(name=subcategory.name, category_id=subcategory.category_id, user_id=current_user.id)
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub

# サブカテゴリ編集
@app.put("/subcategories/{id}", response_model=SubcategoryResponse)
def update_subcategory(id: int, subcategory: SubcategoryCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_sub = db.query(models.Subcategory).filter(
        models.Subcategory.id == id,
        models.Subcategory.user_id == current_user.id
    ).first()
    if not db_sub:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    db_sub.name = subcategory.name
    db_sub.category_id = subcategory.category_id
    db.commit()
    db.refresh(db_sub)
    return db_sub

# サブカテゴリ削除
@app.delete("/subcategories/{id}")
def delete_subcategory(id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_sub = db.query(models.Subcategory).filter(
        models.Subcategory.id == id,
        models.Subcategory.user_id == current_user.id
    ).first()
    if not db_sub:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    db.delete(db_sub)
    db.commit()
    return {"message": "Deleted"}

# ログスキーマ
class LogCreate(BaseModel):
    title: str
    memo: str = None
    memo2: str = None
    subcategory_id: int
    is_public: bool | None = None

class LogResponse(BaseModel):
    id: int
    title: str
    memo: str = None
    memo2: str = None
    subcategory_id: int
    is_public: bool

    class Config:
        from_attributes = True

# ログ一覧取得
@app.get("/logs/{subcategory_id}")
def get_logs(subcategory_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Log).filter(
        models.Log.subcategory_id == subcategory_id,
        models.Log.user_id == current_user.id
    ).all()

# ログ詳細取得
@app.get("/logs/detail/{id}")
def get_log(id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_log = db.query(models.Log).filter(
        models.Log.id == id,
        models.Log.user_id == current_user.id
    ).first()
    if not db_log:
        raise HTTPException(status_code=404, detail="Log not found")
    return db_log

# ログ作成
@app.post("/logs", response_model=LogResponse)
def create_log(log: LogCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    parent_sub = db.query(models.Subcategory).filter(
        models.Subcategory.id == log.subcategory_id,
        models.Subcategory.user_id == current_user.id
    ).first()
    if not parent_sub:
        raise HTTPException(status_code=404, detail="Subcategory not found")

    db_log = models.Log(
        title=log.title,
        memo=log.memo,
        memo2=log.memo2,
        subcategory_id=log.subcategory_id,
        user_id=current_user.id,
        is_public=log.is_public if log.is_public is not None else False
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

# ログ編集
@app.put("/logs/{id}", response_model=LogResponse)
def update_log(id: int, log: LogCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_log = db.query(models.Log).filter(
        models.Log.id == id,
        models.Log.user_id == current_user.id
    ).first()
    if not db_log:
        raise HTTPException(status_code=404, detail="Log not found")
    db_log.title = log.title
    db_log.memo = log.memo
    db_log.memo2 = log.memo2
    db_log.subcategory_id = log.subcategory_id
    if log.is_public is not None:
        db_log.is_public = log.is_public
    db.commit()
    db.refresh(db_log)
    return db_log

# ログ削除
@app.delete("/logs/{id}")
def delete_log(id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_log = db.query(models.Log).filter(
        models.Log.id == id,
        models.Log.user_id == current_user.id
    ).first()
    if not db_log:
        raise HTTPException(status_code=404, detail="Log not found")
    db.delete(db_log)
    db.commit()
    return {"message": "Deleted"}

# 公開ログ一覧取得（認証不要・is_publicのログのみ）
@app.get("/public/logs")
def get_public_logs(db: Session = Depends(get_db)):
    results = db.query(models.Log, models.Subcategory.name, models.Category.name).join(
        models.Subcategory, models.Log.subcategory_id == models.Subcategory.id
    ).join(
        models.Category, models.Subcategory.category_id == models.Category.id
    ).filter(models.Log.is_public == True).order_by(models.Log.created_at.desc()).all()

    return [
        {
            "id": log.id,
            "title": log.title,
            "created_at": log.created_at,
            "category_name": category_name,
            "subcategory_name": subcategory_name,
        }
        for log, subcategory_name, category_name in results
    ]

# 公開ログ詳細取得（認証不要・is_publicのログのみ）
@app.get("/public/logs/{id}")
def get_public_log(id: int, db: Session = Depends(get_db)):
    result = db.query(models.Log, models.Subcategory.name, models.Category.name).join(
        models.Subcategory, models.Log.subcategory_id == models.Subcategory.id
    ).join(
        models.Category, models.Subcategory.category_id == models.Category.id
    ).filter(models.Log.id == id, models.Log.is_public == True).first()

    if not result:
        raise HTTPException(status_code=404, detail="Log not found")

    log, subcategory_name, category_name = result
    return {
        "id": log.id,
        "title": log.title,
        "memo": log.memo,
        "memo2": log.memo2,
        "created_at": log.created_at,
        "category_name": category_name,
        "subcategory_name": subcategory_name,
    }

# フロントエンドの静的ファイルを配信する設定
# directory="../frontend" → backendフォルダから見て一つ上のfrontendフォルダを指定
# html=True → index.htmlをルートURL(/)で表示する設定
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="../frontend", html=True), name="static")