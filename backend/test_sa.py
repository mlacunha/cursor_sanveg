from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class TestModel(Base):
    __tablename__ = 'test'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    @property
    def val(self):
        return getattr(self, '_val', None)

    @val.setter
    def val(self, v):
        self._val = v
        self.name = f"assigned_{v}"

t = TestModel(id=1, val="hello")
print(t.val, t.name)
