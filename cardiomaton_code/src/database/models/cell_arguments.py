from sqlalchemy import Column, Integer, Float, String, Boolean
from src.database.db import Base
import json

class CellArguments(Base):
    __tablename__ = "cell_arguments"

    id = Column(Integer, primary_key=True, autoincrement=True)

    cell_data = Column(String)
    period = Column(Float, nullable=False)
    range = Column(Float, nullable=False)
    self_polarization = Column(Boolean)
    charge_function = Column(String)
    name = Column(String, nullable=False)

    def set_cell_data(self, cell_data):
        self.cell_data = json.dumps(cell_data)
    
    def get_cell_data(self):
        """Get the cell_data as dictionary"""
        return json.loads(self.cell_data) if self.cell_data else {}
    
    def to_dict(self):
        return {
            "id": self.id,
            "cell_data": self.get_cell_data(),
            "period": self.period,
            "range": self.range,
            "self_polarization": self.self_polarization,
            "charge_function": self.charge_function, 
            "name": self.name
        }
    