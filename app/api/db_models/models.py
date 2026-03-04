from http import HTTPStatus

from sqlalchemy import String, Integer, Column, Boolean, JSON

from core.base_class import Base


class RuleModel(Base):
    __tablename__ = "rule"

    id = Column(Integer, autoincrement=True, primary_key=True)
    description = Column(String, nullable=True)
    method = Column(String, nullable=False)
    url = Column(String, nullable=False)
    call_backend = Column(Boolean, default=True)
    custom_headers = Column(JSON, default=None)
    status_code = Column(Integer, default=HTTPStatus.OK)
    response = Column(String, nullable=True)
    response_media_type = Column(String, default='application/json', nullable=True)
    enable = Column(Boolean, default=True)
    mock_count = Column(Integer, nullable=True, default=-1)
    response_delay = Column(Integer, default=0)
