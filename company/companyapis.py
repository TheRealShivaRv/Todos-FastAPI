from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_company_name():
    return {"company_name": "Marthandam Ganesh"}


@router.get("/employees")
async def get_employee_count():
    return 256
