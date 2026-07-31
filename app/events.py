from fastapi import APIRouter
from app.database import *
from app.models import OutreachEvent

events = APIRouter()