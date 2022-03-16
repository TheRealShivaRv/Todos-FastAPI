from database import Base
from sqlalchemy import Column, Boolean, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

# The todos property in Users class and owner property in Todo class are
# SQL Alchemy's special variables and not a column in the database


class Users(Base):
    __tablename__ = 'Users'

    id = Column(Integer, index=True, primary_key=True)
    email = Column(String(256))
    username = Column(String(256))
    first_name = Column(String(128))
    last_name = Column(String(128))
    hashed_password = Column(String(256))
    is_active = Column(Boolean, default=True)

    todos = relationship('Todo', back_populates='owner')


class Todo(Base):
    __tablename__ = 'Todos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256))
    description = Column(String(256))
    priority = Column(Integer)
    is_done = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey(Users.id))

    owner = relationship('Users', back_populates='todos')


"""
SQL Practice

Creating a new todo - Inseting a row into  a table

INSERT INTO Todo(title,description,priority,is_done) VALUES ('Haircut','Need to get length 1mm',3,False)

Performing queries

SELECT * FROM Todos - Brings the whole table
SELECT title FROM Todos - Brings only the title column 
SELECT title,description FROM Todos - Brings two columns from the table a.k.a Multiple Column querying

Filtering results using WHERE

SELECT * FROM TodoS WHERE priority = 5;

Updating a Row
UPDATE Todos SET complete = True WHERE id = 5;
Delete Records in Table
DELETE FROM Todos WHERE id = 5; - Deletes a single rows with id (Primary Key) = 5

Delete multiple rows in the table
DELETE FROM Todos WHERE complete=0; Deletes all rows where complete is marked false

Deleting a Table
DROP TABLE Todos;
"""
