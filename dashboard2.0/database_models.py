from sqlalchemy import Column, String, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Group(Base):
    __tablename__ = "groups"
    name = Column(String, primary_key=True)

    clients = relationship("Client", back_populates="group")
    policies = relationship("Policy", back_populates="group")

class Category(Base):
    __tablename_ = "categories"
    name = Column(String, primary_key=True)

    policies = relationship("Policy", back_populates="category")
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
    allowed = Column(Integer, nullable=False)
    __table_args__ = (CheckConstraint("allowed in (0,1)", name="allowed_check"),)

    group = relationship("Group", back_populates="policies")
    category_rel = relationship("Category", back_populates="policies")


class Domain(Base):
    __tablename__ = "domains"
    domain = Column(String, primary_key=True)
    category = Column(String, ForeignKey("categories.name", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)

    category_rel = relationship("Category", back_populates="domains")