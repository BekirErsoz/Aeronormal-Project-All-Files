from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class ImageData(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    timestamp = Column(Float)

engine = create_engine('sqlite:///drone_data.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def init_db():
    Base.metadata.create_all(engine)

def store_image_data(filename, timestamp):
    new_image = ImageData(filename=filename, timestamp=timestamp)
    session.add(new_image)
    session.commit()

def get_all_images():
    return session.query(ImageData).all()