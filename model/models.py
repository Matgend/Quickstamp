from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from .database import Base
import datetime

#Users table
class User(Base):

    __tablename__ = 'users' 

    #Table structure

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    weekly_working_time: Mapped[float]
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default = datetime.datetime.now)

    #Relations one to many
    timestamps_user_entries: Mapped[list['Timestamp']] = relationship(back_populates = 'user', cascade = 'all, delete-orphan')


#Companies table
class Company(Base):

    __tablename__ = 'companies'

    #Table structure
    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    company_name: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default = datetime.datetime.now)

    #Relations one to many
    timestamps_comp_entries: Mapped[list['Timestamp']] = relationship(back_populates = 'company', cascade = 'all, delete-orphan')


#Timestamps table
class Timestamp(Base):

    __tablename__ = 'timestamps'

    #Table structure
    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    status: Mapped[str]
    time: Mapped[str] #format hh:mm:ss
    date: Mapped[str] #format dd/mm/yyyy
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    company_id: Mapped[int] = mapped_column(ForeignKey('companies.id'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default = datetime.datetime.now)

    #Relations many to one
    user: Mapped[User] = relationship(back_populates = 'timestamps_user_entries')
    company: Mapped[Company] = relationship(back_populates = 'timestamps_comp_entries')
