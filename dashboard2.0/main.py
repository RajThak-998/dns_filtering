from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from models import Groups, Categories, Clients, Domains, Policies
from database_models import Base, Group, Category, Client, Domain, Policy
from database import engine, SessionLocal

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def root():
    return {
        "message": "DNS Filtering API",
        "docs": "/docs",
        "version": "1.0.0"
    }

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/group", response_model=Groups)
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
    

@app.get("/group", response_model=list[Groups])
def get_groups(db: Session = Depends(get_db)):
    groups = db.query(Group).all()
    return groups

@app.get("/group/{group_name}", response_model=Groups)
def get_group(group_name: str, db: Session = Depends(get_db)):
    group = db.get(Group, group_name)
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@app.put("/group/{group_name}", response_model=Groups)
def update_group(group_name: str, updated_group: Groups, db: Session = Depends(get_db)):
    group = db.get(Group, group_name)
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    
    try:
        group.name = updated_group.name
        db.commit()
        db.refresh(group)
        return group
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Group name already exists")
    
@app.delete("/group/{group_name}")
def delete_group(group_name: str, db: Session = Depends(get_db)):
    """
    Delete a group by name.
    Checks for references in clients and policies before deleting.
    """
    group = db.get(Group, group_name)
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if group is referenced by any clients
    client_count = db.query(Client).filter(Client.client_group == group_name).count()
    if client_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete group: it is referenced by {client_count} client(s)"
        )
    
    # Check if group is referenced by any policies
    policy_count = db.query(Policy).filter(Policy.client_group == group_name).count()
    if policy_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete group: it is referenced by {policy_count} policy(ies)"
        )
    
    # Safe to delete
    db.delete(group)
    db.commit()
    return {"message": f"Group '{group_name}' deleted successfully"}


# Category

@app.post("/category", response_model=Categories)
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
    
@app.get("/category", response_model=list[Categories])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return categories

@app.get("/category/{cat_name}", response_model=Categories)
def get_category(cat_name: str, db: Session = Depends(get_db)):
    category = db.get(Category, cat_name)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@app.put("/category/{cat_name}", response_model=Categories)
def update_category(cat_name: str, updated_cat: Categories, db: Session = Depends(get_db)):
    category = db.get(Category, cat_name)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    try:
        category.name = updated_cat.name
        db.commit()
        db.refresh(category)
        return category
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail = "Category name already exists")
    
@app.delete("/category/{cat_name}")
def delete_category(cat_name: str, db: Session = Depends(get_db)):
    """
    Delete a category by name.
    Checks for references in domains and policies before deleting.
    """
    category = db.get(Category, cat_name)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if category is referenced by any domains
    domain_count = db.query(Domain).filter(Domain.category == cat_name).count()
    if domain_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete category: it is referenced by {domain_count} domain(s)"
        )
    
    # Check if category is referenced by any policies
    policy_count = db.query(Policy).filter(Policy.category == cat_name).count()
    if policy_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete category: it is referenced by {policy_count} policy(ies)"
        )
    
    # Safe to delete
    db.delete(category)
    db.commit()
    return {"message": f"Category '{cat_name}' deleted successfully"}
    
    


#Clients



@app.post("/client", response_model=Clients)
def create_client(client: Clients, db: Session = Depends(get_db)):
    db_client = Client(ip=client.ip, client_group=client.client_group)
    try:
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
        return db_client
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Client already exists or Invalid group")   
    
@app.get("/client", response_model=list[Clients])
def get_clients(db: Session = Depends(get_db)):
    clients = db.query(Client).all()
    return clients

@app.get("/client/{ip}", response_model = Clients)
def get_client(ip: str, db: Session = Depends(get_db)):
    client = db.get(Client, ip)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@app.put("/client/{ip}", response_model=Clients)
def update_client(ip: str, updated_client: Clients, db: Session = Depends(get_db)):
    client = db.get(Client, ip)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    
    try: 
        client.ip = updated_client.ip
        client.client_group = updated_client.client_group
        db.commit()
        db.refresh(client)
        return client
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="IP already exists or Invalid group reference")
    
@app.delete("/client/{ip}")
def delete_client(ip: str, db:Session = Depends(get_db)):
    client = db.get(Client, ip)
    if client is None:
        raise HTTPException(status_code=404, detail = "Client not found")
    
    db.delete(client)
    db.commit()
    return {"message": f"Client '{ip}' deleted successfully"}



#Domains


@app.post("/domain", response_model=Domains)
def create_domain(domain: Domains, db: Session = Depends(get_db)):
    db_domain = Domain(domain = domain.domain, category = domain.category)
    try:
        db.add(db_domain)
        db.commit()
        db.refresh(db_domain)
        return db_domain
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Domain already exists or Invalid category")
    
@app.get("/domain", response_model=list[Domains])
def get_domains(db: Session = Depends(get_db)):
    domains = db.query(Domain).all()
    return domains

@app.get("/domain/{name}", response_model=Domains)
def get_domain(name: str, db: Session =Depends(get_db)):
    domain = db.get(Domain, name)
    if domain is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    return domain

@app.put("/domain/{name}", response_model=Domains)
def update_domain(name: str, updated_domain: Domains, db: Session = Depends(get_db)):
    domain = db.get(Domain, name)
    if domain is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    try:
        domain.domain = updated_domain.domain
        domain.category = updated_domain.category
        db.commit()
        db.refresh(domain)
        return domain
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Domain name already exists or invalid category reference")
    
@app.delete("/domain/{name}")
def delete_domain(name:str, db:Session = Depends(get_db)):
    domain = db.get(Domain, name)
    if domain is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    db.delete(domain)
    db.commit()
    return {"message": f"Domain '{name}' deleted successfully"}




#Policy
    
@app.post("/policy", response_model=Policies)
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
        raise HTTPException(status_code=400, detail="Policy already exists or invalid references")
    

@app.get("/policy", response_model=list[Policies])
def get_policies(db: Session = Depends(get_db)):
    policies = db.query(Policy).all()
    return policies

@app.get("/policy/{group}/{category}", response_model=Policies)
def get_policy(group: str, category: str, db: Session = Depends(get_db)):
    policy = db.query(Policy).filter(Policy.client_group==group, Policy.category==category).first()
    if policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

@app.patch("/policy/{client_group}/{category}", response_model=Policies)
def patch_policy(
    client_group: str, 
    category: str, 
    updated_policy: Policies, 
    db: Session = Depends(get_db)
):
    """
    Patch (partial update) a policy.
    Only updates the 'allowed' field - primary keys cannot be changed.
    If you need to change group/category, delete and create a new policy.
    """
    policy = db.query(Policy).filter(
        Policy.client_group == client_group,
        Policy.category == category
    ).first()
    
    if policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    # Validate that primary keys in body match the URL
    if (updated_policy.client_group != client_group or 
        updated_policy.category != category):
        raise HTTPException(
            status_code=400, 
            detail="Cannot change primary keys via PATCH. Use DELETE + POST instead."
        )
    
    # Only update the allowed field 
    policy.allowed = updated_policy.allowed
    db.commit()
    db.refresh(policy)
    return policy

@app.delete("/policy/{group}/{category}")
def delete_policy(group: str, category: str, db: Session = Depends(get_db)):
    policy = db.query(Policy).filter(Policy.client_group==group, Policy.category==category).first()
    if policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    db.delete(policy)
    db.commit()
    return {"message": f"Policy for group '{group}' and category '{category}' deleted successfully"}


# Additional endpoints

# Get all clients in a specific group
@app.get("/group/{group_name}/clients", response_model=list[Clients])
def get_group_clients(group_name: str, db: Session = Depends(get_db)):
    """Get all clients belonging to a specific group"""
    clients = db.query(Client).filter(Client.client_group == group_name).all()
    return clients

# Get all domains in a specific category
@app.get("/category/{cat_name}/domains", response_model=list[Domains])
def get_category_domains(cat_name: str, db: Session = Depends(get_db)):
    """Get all domains in a specific category"""
    domains = db.query(Domain).filter(Domain.category == cat_name).all()
    return domains

# Get all policies for a specific group
@app.get("/group/{group_name}/policies", response_model=list[Policies])
def get_group_policies(group_name: str, db: Session = Depends(get_db)):
    """Get all policies for a specific group"""
    policies = db.query(Policy).filter(Policy.client_group == group_name).all()
    return policies