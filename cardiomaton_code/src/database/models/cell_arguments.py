from sqlalchemy import Column, Integer, Float, String
from src.database.db import Base

class CellArguments(Base):
    __tablename__ = "cell_arguments"

    id = Column(Integer, primary_key=True, autoincrement=True)

    V_rest = Column(Float, nullable=False)
    V_thresh = Column(Float, nullable=False)
    V_peak = Column(Float, nullable=False)
    t_thresh = Column(Float, nullable=False)
    t_peak = Column(Float, nullable=False)
    t_end = Column(Float, nullable=False)
    eps = Column(Float, nullable=False)
    period = Column(Float, nullable=False)
    duration = Column(Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "V_rest": self.V_rest,
            "V_thresh": self.V_thresh,
            "V_peak": self.V_peak,
            "t_thresh": self.t_thresh,
            "t_peak": self.t_peak,
            "t_end": self.t_end,
            "eps": self.eps,
            "period": self.period,
            "duration": self.duration,
        }
    