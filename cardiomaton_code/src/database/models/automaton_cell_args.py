from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
from src.database.db import Base
from src.database.models.cell_arguments import CellArguments
from src.database.models.automaton import AutomatonTable

class AutomatonCellArgs(Base):
    __tablename__ = "automaton_cell_args"
    id = Column(Integer, primary_key=True, autoincrement=True)

    automaton_id = Column(Integer, ForeignKey("automaton_table.id", ondelete="CASCADE"), nullable=False)
    arg_id = Column(Integer, ForeignKey("cell_arguments.id", ondelete="RESTRICT"), nullable=False)

    __table_args__ = (UniqueConstraint("automaton_id", "arg_id", name="uix_automaton_arg"),)

    def __repr__(self) -> str:
        return f"<AutomatonCellArgs(id={self.id} automaton_id={self.automaton_id} arg_id={self.arg_id})>"
