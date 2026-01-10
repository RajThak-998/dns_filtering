from sqlalchemy import Column, Index, String, Integer, ForeignKey, CheckConstraint, Boolean
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Group(Base):
    __tablename__ = "groups"
    name = Column(String, primary_key=True)

    clients = relationship("Client", back_populates="group")
    policies = relationship("Policy", back_populates="group")

class Category(Base):
    __tablename__ = "categories"
    name = Column(String, primary_key=True)

    policies = relationship("Policy", back_populates="category_rel")
    domains = relationship("Domain", back_populates="category_rel")

class Client(Base):
    __tablename__ = "clients"
    ip = Column(String, primary_key=True)
    client_group = Column(String, ForeignKey("groups.name", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)

    group = relationship("Group", back_populates="clients")

class Policy(Base):
    __tablename__ = "policies"
    client_group = Column(String, ForeignKey("groups.name", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    category = Column(String, ForeignKey("categories.name", onupdate="CASCADE", ondelete="RESTRICT"), primary_key=True)
    allowed = Column(Boolean, nullable=False)
    

    group = relationship("Group", back_populates="policies")
    category_rel = relationship("Category", back_populates="policies")

class Domain(Base):
    __tablename__ = "domains"
    __table_args__ = (Index("idx_domain_category", "category"),)
    domain = Column(String, primary_key=True)
    category = Column(String, ForeignKey("categories.name", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)

    category_rel = relationship("Category", back_populates="domains")