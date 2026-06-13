from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, get_db
from pydantic import BaseModel
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

# カテゴリ一覧取得
@app.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()

# カテゴリ作成
@app.post("/categories", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = models.Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# カテゴリ編集
@app.put("/categories/{id}", response_model=CategoryResponse)
def update_category(id: int, category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = db.query(models.Category).filter(models.Category.id == id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    db_category.name = category.name
    db.commit()
    db.refresh(db_category)
    return db_category

# カテゴリ削除
@app.delete("/categories/{id}")
def delete_category(id: int, db: Session = Depends(get_db)):
    db_category = db.query(models.Category).filter(models.Category.id == id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(db_category)
    db.commit()
    return {"message": "Deleted"}

# サブカテゴリスキーマ
class SubcategoryCreate(BaseModel):
    name: str
    category_id: int

class SubcategoryResponse(BaseModel):
    id: int
    name: str
    category_id: int

    class Config:
        from_attributes = True

# サブカテゴリ一覧取得
@app.get("/subcategories/{category_id}")
def get_subcategories(category_id: int, db: Session = Depends(get_db)):
    return db.query(models.Subcategory).filter(models.Subcategory.category_id == category_id).all()

# サブカテゴリ作成
@app.post("/subcategories", response_model=SubcategoryResponse)
def create_subcategory(subcategory: SubcategoryCreate, db: Session = Depends(get_db)):
    db_sub = models.Subcategory(name=subcategory.name, category_id=subcategory.category_id)
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub

# サブカテゴリ編集
@app.put("/subcategories/{id}", response_model=SubcategoryResponse)
def update_subcategory(id: int, subcategory: SubcategoryCreate, db: Session = Depends(get_db)):
    db_sub = db.query(models.Subcategory).filter(models.Subcategory.id == id).first()
    if not db_sub:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    db_sub.name = subcategory.name
    db_sub.category_id = subcategory.category_id
    db.commit()
    db.refresh(db_sub)
    return db_sub

# サブカテゴリ削除
@app.delete("/subcategories/{id}")
def delete_subcategory(id: int, db: Session = Depends(get_db)):
    db_sub = db.query(models.Subcategory).filter(models.Subcategory.id == id).first()
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

class LogResponse(BaseModel):
    id: int
    title: str
    memo: str = None
    memo2: str = None
    subcategory_id: int

    class Config:
        from_attributes = True

# ログ一覧取得
@app.get("/logs/{subcategory_id}")
def get_logs(subcategory_id: int, db: Session = Depends(get_db)):
    return db.query(models.Log).filter(models.Log.subcategory_id == subcategory_id).all()

# ログ詳細取得
@app.get("/logs/detail/{id}")
def get_log(id: int, db: Session = Depends(get_db)):
    db_log = db.query(models.Log).filter(models.Log.id == id).first()
    if not db_log:
        raise HTTPException(status_code=404, detail="Log not found")
    return db_log

# ログ作成
@app.post("/logs", response_model=LogResponse)
def create_log(log: LogCreate, db: Session = Depends(get_db)):
    db_log = models.Log(title=log.title, memo=log.memo, memo2=log.memo2, subcategory_id=log.subcategory_id)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

# ログ編集
@app.put("/logs/{id}", response_model=LogResponse)
def update_log(id: int, log: LogCreate, db: Session = Depends(get_db)):
    db_log = db.query(models.Log).filter(models.Log.id == id).first()
    if not db_log:
        raise HTTPException(status_code=404, detail="Log not found")
    db_log.title = log.title
    db_log.memo = log.memo
    db_log.memo2 = log.memo2
    db_log.subcategory_id = log.subcategory_id
    db.commit()
    db.refresh(db_log)
    return db_log

# ログ削除
@app.delete("/logs/{id}")
def delete_log(id: int, db: Session = Depends(get_db)):
    db_log = db.query(models.Log).filter(models.Log.id == id).first()
    if not db_log:
        raise HTTPException(status_code=404, detail="Log not found")
    db.delete(db_log)
    db.commit()
    return {"message": "Deleted"}

# フロントエンドの静的ファイルを配信する設定
# directory="../frontend" → backendフォルダから見て一つ上のfrontendフォルダを指定
# html=True → index.htmlをルートURL(/)で表示する設定
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="../frontend", html=True), name="static")