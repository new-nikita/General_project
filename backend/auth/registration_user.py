from fastapi import APIRouter, HTTPException
from authx import AuthX, AuthXConfig

router = APIRouter(tags=["Users"])


@router.post('/login')
def login():
    return 'login'


@router.get('/protected')
def protected():
    return 'protected'

