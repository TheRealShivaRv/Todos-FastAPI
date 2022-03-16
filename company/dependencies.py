from fastapi import Header
from fastapi.exceptions import HTTPException


async def get_dependencies(token: str = Header(...)):
    if token != 'allowed':
        raise HTTPException(status_code=403, detail={
                            'Forbidden': 'Invalid Internal Token'})
