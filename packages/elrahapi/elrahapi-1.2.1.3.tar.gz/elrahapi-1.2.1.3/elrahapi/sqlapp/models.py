# from sqlalchemy import (
#     Boolean,
#     Column,
#     DECIMAL,
#     Integer,
#     String,
#     Text,
#     DateTime,
#     ForeignKey,
#     Table,
# )

# from settings.database import Base

# from sqlalchemy.sql import func
# from sqlalchemy.orm import relationship


# class Entity(Base):
#     __tablename__ = 'entities'
#     id = Column(Integer, primary_key=True)
#     date_created = Column(DateTime, default=func.now())
#     date_updated = Column(DateTime,default=func.now(), onupdate=func.now())
#     is_deleted = Column(Boolean, nullable=False,default=False)
#     date_deleted = Column(DateTime, nullable=True)
