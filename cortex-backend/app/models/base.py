from typing import TypeVar, Type, List, Optional

from sqlmodel import SQLModel, select

from app.core.context import get_db

T = TypeVar("T", bound="ActiveModel")


class ActiveModel(SQLModel):
    """
    让 SQLModel 支持类似 Django 的 Active Record 操作模式
    """

    def save(self: T) -> T:
        """保存或更新当前实例"""
        db = get_db()
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def delete(self) -> None:
        """删除当前实例"""
        db = get_db()
        db.delete(self)
        db.commit()

    @classmethod
    def create(cls: Type[T], **kwargs) -> T:
        """创建并保存新实例"""
        instance = cls(**kwargs)
        return instance.save()

    @classmethod
    def by_id(cls: Type[T], id: int) -> Optional[T]:
        """根据 ID 获取"""
        db = get_db()
        return db.get(cls, id)

    @classmethod
    def all(cls: Type[T]) -> List[T]:
        """获取所有记录"""
        db = get_db()
        return db.exec(select(cls)).all()

    @classmethod
    def where(cls: Type[T], **kwargs) -> Optional[T]:
        """简单的按条件查询第一个 (例如: User.where(email="..."))"""
        db = get_db()
        statement = select(cls)
        for key, value in kwargs.items():
            statement = statement.where(getattr(cls, key) == value)
        return db.exec(statement).first()