# RUN THIS FILE ONCE TO CREATE THE DATABASE AND TABLES!


from sqlmodel import SQLModel
from database.database import get_engine
import database.tables

#SQLModel.metadata.drop_all(get_engine())
SQLModel.metadata.create_all(get_engine())

