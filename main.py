from sanic import Sanic
import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base

db = create_engine(config.DATABASE_URI)
Base.metadata.create_all(db)
make_session = sessionmaker(bind=db)

app = Sanic()

from app.routes import *


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
