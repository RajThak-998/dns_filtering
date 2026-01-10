from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from models import Groups, Categories, Clients, Domains, Policies
from database_models import Base, Group, Category, Client, Domain, Policy
from database import engine, SessionLocal

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/groups/", response_model=Groups)
def create_group(group: Groups, db: Session = Depends(get_db)):
    db_group = Group(name=group.name)
    try:
        db.add(db_group)
        db.commit()
        db.refresh(db_group)
        return db_group
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Group already exists")

@app.post("/categories/", response_model=Categories)
def create_category(category: Categories, db: Session = Depends(get_db)):
    db_category = Category(name = category.name)
    try:
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Category already exists") 

@app.post("/clients/", response_model=Clients)
def create_client(client: Clients, db: Session = Depends(get_db)):
    db_client = Client(ip=client.ip, client_group=client.client_group)
    try:
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
        return db_client
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Client already exists or Invalis group")   

@app.post("/domains/", response_model=Domains)
def create_domain(domain: Domains, db: Session = Depends(get_db)):
    db_domain = Domain(domain = domain.domain, category = domain.category)
    try:
        db.add(db_domain)
        db.commit()
        db.refresh(db_domain)
        return db_domain
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Domain already exists or Invalid group")
    
@app.post("/policies/", response_model=Policies)
def create_policy(policy : Policies, db: Session = Depends(get_db)):
    db_policy = Policy(
        client_group = policy.client_group,
        category = policy.category,
        allowed = policy.allowed
    )   

    try:
        db.add(db_policy)
        db.commit()
        db.refresh(db_policy)
        return db_policy
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Policy already exists or invalis references")

