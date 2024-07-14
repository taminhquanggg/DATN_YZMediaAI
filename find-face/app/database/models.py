from sqlalchemy import Column, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

from app.database.custom_types import Cube



Base = declarative_base()
class_cache = {}

class Face(Base):
    __tablename__ = "faces"
    __table_args__ = {'extend_existing': True}

    AutoID = Column(Integer, primary_key=True)
    ID = Column(String)
    ImageID = Column(String)
    ImageDetectID = Column(String)
    ImageDetectPath = Column(String)
    FaceDetectID = Column(String)
    FaceDetectPath = Column(String)
    Embedding = Column(Cube)
    CreateAt = Column(DateTime)
    UpdateAt = Column(DateTime)
    __table_args__ = (UniqueConstraint("ID"),)

    def __repr__(self):
        return "<Face(ID='%s', ImageID='%d')>" % (
            self.ID,
            self.ImageID
        )

def get_class(table_name):
    global Base, class_cache

    if table_name in class_cache:
        return class_cache[table_name]

    class BaseClass(Base):
        __tablename__ = table_name
        __table_args__ = {'extend_existing': True}

        AutoID = Column(Integer, primary_key=True)
        ID = Column(String)
        ImageID = Column(String)
        ImageDetectID = Column(String)
        ImageDetectPath = Column(String)
        FaceDetectID = Column(String)
        FaceDetectPath = Column(String)
        Embedding = Column(Cube)
        CreateAt = Column(DateTime)
        UpdateAt = Column(DateTime)
        __table_args__ = (UniqueConstraint("ID"),)

    def __repr__(self):
        return "<Face(ID='%s', ImageID='%d')>" % (
            self.ID,
            self.ImageID
        )
    
    class_cache[table_name] = BaseClass
    
    return BaseClass
