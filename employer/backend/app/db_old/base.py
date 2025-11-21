from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr

class Base(DeclarativeBase):
    __abstract__ = True

    # Автоматически генерируемое имя таблицы
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"
    
    # Создаем id
    # id: Mapped[int] = mapped_column(primary_key=True)

