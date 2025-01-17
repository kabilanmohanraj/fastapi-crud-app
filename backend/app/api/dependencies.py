from typing import Annotated

from fastapi import Depends

from backend.app.api.routes.login import get_current_user
from backend.app.models import User


CurrentUser = Annotated[User, Depends(get_current_user)]