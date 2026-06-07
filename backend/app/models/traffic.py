from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class VehicleType(Base):
    __tablename__ = "vehicle_types"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True)
    label = Column(String(100))

class Violation(Base):
    __tablename__ = "violations"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), unique=True, index=True)
    name = Column(String(150))
    default_vehicle_type = Column(String(20))
    
    fines = relationship("FineByState", back_populates="violation", cascade="all, delete-orphan")
    sections = relationship("LawSection", back_populates="violation", cascade="all, delete-orphan")

class LawSection(Base):
    __tablename__ = "law_sections"
    id = Column(Integer, primary_key=True, index=True)
    violation_id = Column(Integer, ForeignKey("violations.id"))
    section_code = Column(String(50))
    act_name = Column(String(100))
    penalty_details = Column(Text)
    
    violation = relationship("Violation", back_populates="sections")

class FineByState(Base):
    __tablename__ = "fines_by_state"
    id = Column(Integer, primary_key=True, index=True)
    violation_id = Column(Integer, ForeignKey("violations.id"))
    state = Column(String(100), index=True)  # empty or 'National' for central laws
    vehicle_type = Column(String(20))
    fine_min = Column(Integer)
    fine_max = Column(Integer)
    fine_repeat_min = Column(Integer, nullable=True)
    fine_repeat_max = Column(Integer, nullable=True)
    details = Column(Text)
    
    violation = relationship("Violation", back_populates="fines")
