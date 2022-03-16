from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Database URL - in this local file directory
# SQL_DATABASE_URL = 'sqlite:///./todos.db' --- sqlite setting
# SQL_DATABASE_URL = 'postgresql://postgres:123456@localhost/TodoApplicationDatabase' -- postgres setting
SQL_DATABASE_URL = 'mysql+pymysql://root:123456@127.0.0.1:3306/todoapp'

# Creating a connection - SQLITE Setting
# engine = create_engine(
#     SQL_DATABASE_URL, connect_args={'check_same_thread': False}
# )
# Creating a connection - PostgreSQL Setting
engine = create_engine(
    SQL_DATABASE_URL
)

# Creating a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the template model for creating our custom database models. Similar to models.Model in django
Base = declarative_base()
