from typing import Annotated

from fastapi import Depends

from app.api.routes.login import get_current_user
from app.models import User


CurrentUser = Annotated[User, Depends(get_current_user)]