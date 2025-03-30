from fastapi import APIRouter


router = APIRouter(tags=["Users"])


@router.get('/main')
async def hellos():
    return 'Hello World'
