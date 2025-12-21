from contextvars import ContextVar

from sqlmodel import Session

# 定义一个全局的 ContextVar，用来存储当前请求的 Session
# ContextVar 是线程/协程安全的，不同请求之间不会混淆
_db_session: ContextVar[Session] = ContextVar("db_session")

def set_db_session(session: Session):
    _db_session.set(session)

def get_db() -> Session:
    try:
        return _db_session.get()
    except LookupError:
        raise RuntimeError("Session context is not initialized. Are you outside of a request?")
