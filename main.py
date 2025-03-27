from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.security import OAuth2PasswordBearer
from firebase_admin import credentials, auth, firestore, initialize_app
from pydantic import BaseModel
from typing import Optional, List
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firebase
cred = credentials.Certificate("firebase_credentials.json")
try:
    initialize_app(cred)
    logger.info("Firebase initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Firebase: {e}")
db = firestore.client()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve HTML templates
@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("templates/index.html") as f:
        return f.read()

@app.get("/login", response_class=HTMLResponse)
def login_page():
    with open("templates/login.html") as f:
        return f.read()

@app.get("/add_driver", response_class=HTMLResponse)
def add_driver_page():
    with open("templates/add_driver.html") as f:
        return f.read()

@app.get("/add_team", response_class=HTMLResponse)
def add_team_page():
    with open("templates/add_team.html") as f:
        return f.read()

@app.get("/query_drivers", response_class=HTMLResponse)
def query_drivers_page():
    with open("templates/query_drivers.html") as f:
        return f.read()

@app.get("/query_teams", response_class=HTMLResponse)
def query_teams_page():
    with open("templates/query_teams.html") as f:
        return f.read()

@app.get("/driver_detail", response_class=HTMLResponse)
def driver_detail_page():
    with open("templates/driver_detail.html") as f:
        return f.read()

@app.get("/team_detail", response_class=HTMLResponse)
def team_detail_page():
    with open("templates/team_detail.html") as f:
        return f.read()

@app.get("/compare_drivers", response_class=HTMLResponse)
def compare_drivers_page():
    with open("templates/compare_drivers.html") as f:
        return f.read()

@app.get("/compare_teams", response_class=HTMLResponse)
def compare_teams_page():
    with open("templates/compare_teams.html") as f:
        return f.read()

# Pydantic Models
class Driver(BaseModel):
    name: str
    age: int
    total_pole_positions: int
    total_race_wins: int
    total_points_scored: int
    total_world_titles: int
    total_fastest_laps: int
    team: str

class Team(BaseModel):
    name: str
    year_founded: int
    total_pole_positions: int
    total_race_wins: int
    total_constructor_titles: int
    finishing_position_last_season: int

# Authentication function
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        decoded_token = auth.verify_id_token(token)
        logger.info("Token verified successfully")
        return decoded_token
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid authentication credentials: {str(e)}")

# CRUD Endpoints with logging
@app.post("/drivers/")
def add_driver(driver: Driver, user: dict = Depends(get_current_user)):
    try:
        driver_ref = db.collection("drivers").document(driver.name)
        if driver_ref.get().exists:
            raise HTTPException(status_code=400, detail="Driver already exists")
        driver_ref.set(driver.dict())
        logger.info(f"Driver {driver.name} added successfully")
        return {"message": "Driver added successfully"}
    except Exception as e:
        logger.error(f"Failed to add driver: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add driver: {str(e)}")

@app.post("/teams/")
def add_team(team: Team, user: dict = Depends(get_current_user)):
    try:
        team_ref = db.collection("teams").document(team.name)
        if team_ref.get().exists:
            raise HTTPException(status_code=400, detail="Team already exists")
        team_ref.set(team.dict())
        logger.info(f"Team {team.name} added successfully")
        return {"message": "Team added successfully"}
    except Exception as e:
        logger.error(f"Failed to add team: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add team: {str(e)}")

@app.get("/drivers/{name}", response_model=Driver)
def get_driver(name: str):
    try:
        driver_ref = db.collection("drivers").document(name).get()
        if not driver_ref.exists:
            raise HTTPException(status_code=404, detail="Driver not found")
        logger.info(f"Driver {name} retrieved successfully")
        return driver_ref.to_dict()
    except Exception as e:
        logger.error(f"Failed to get driver: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get driver: {str(e)}")

@app.get("/teams/{name}", response_model=Team)
def get_team(name: str):
    try:
        team_ref = db.collection("teams").document(name).get()
        if not team_ref.exists:
            raise HTTPException(status_code=404, detail="Team not found")
        logger.info(f"Team {name} retrieved successfully")
        return team_ref.to_dict()
    except Exception as e:
        logger.error(f"Failed to get team: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get team: {str(e)}")

@app.get("/drivers/query/")
def query_drivers(attribute: str, comparison: str, value: int):
    try:
        drivers_ref = db.collection("drivers")
        if comparison == "lt":
            query = drivers_ref.where(attribute, "<", value)
        elif comparison == "gt":
            query = drivers_ref.where(attribute, ">", value)
        elif comparison == "eq":
            query = drivers_ref.where(attribute, "==", value)
        else:
            raise HTTPException(status_code=400, detail="Invalid comparison operator")
        result = [doc.to_dict() for doc in query.stream()]
        logger.info(f"Queried drivers with {attribute} {comparison} {value}: {len(result)} results")
        return result
    except Exception as e:
        logger.error(f"Failed to query drivers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to query drivers: {str(e)}")

@app.get("/teams/query/")
def query_teams(attribute: str, comparison: str, value: int):
    try:
        teams_ref = db.collection("teams")
        if comparison == "lt":
            query = teams_ref.where(attribute, "<", value)
        elif comparison == "gt":
            query = teams_ref.where(attribute, ">", value)
        elif comparison == "eq":
            query = teams_ref.where(attribute, "==", value)
        else:
            raise HTTPException(status_code=400, detail="Invalid comparison operator")
        result = [doc.to_dict() for doc in query.stream()]
        logger.info(f"Queried teams with {attribute} {comparison} {value}: {len(result)} results")
        return result
    except Exception as e:
        logger.error(f"Failed to query teams: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to query teams: {str(e)}")

@app.put("/drivers/{name}")
def update_driver(name: str, driver: Driver, user: dict = Depends(get_current_user)):
    try:
        driver_ref = db.collection("drivers").document(name)
        if not driver_ref.get().exists:
            raise HTTPException(status_code=404, detail="Driver not found")
        driver_ref.update(driver.dict())
        logger.info(f"Driver {name} updated successfully")
        return {"message": "Driver updated successfully"}
    except Exception as e:
        logger.error(f"Failed to update driver: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update driver: {str(e)}")

@app.put("/teams/{name}")
def update_team(name: str, team: Team, user: dict = Depends(get_current_user)):
    try:
        team_ref = db.collection("teams").document(name)
        if not team_ref.get().exists:
            raise HTTPException(status_code=404, detail="Team not found")
        team_ref.update(team.dict())
        logger.info(f"Team {name} updated successfully")
        return {"message": "Team updated successfully"}
    except Exception as e:
        logger.error(f"Failed to update team: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update team: {str(e)}")

@app.delete("/drivers/{name}")
def delete_driver(name: str, user: dict = Depends(get_current_user)):
    try:
        driver_ref = db.collection("drivers").document(name)
        if not driver_ref.get().exists:
            raise HTTPException(status_code=404, detail="Driver not found")
        driver_ref.delete()
        logger.info(f"Driver {name} deleted successfully")
        return {"message": "Driver deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete driver: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete driver: {str(e)}")

@app.delete("/teams/{name}")
def delete_team(name: str, user: dict = Depends(get_current_user)):
    try:
        team_ref = db.collection("teams").document(name)
        if not team_ref.get().exists:
            raise HTTPException(status_code=404, detail="Team not found")
        team_ref.delete()
        logger.info(f"Team {name} deleted successfully")
        return {"message": "Team deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete team: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete team: {str(e)}")

@app.get("/compare/drivers/")
def compare_drivers(driver1: str, driver2: str):
    try:
        ref1 = db.collection("drivers").document(driver1).get()
        ref2 = db.collection("drivers").document(driver2).get()
        if not ref1.exists or not ref2.exists:
            raise HTTPException(status_code=404, detail="One or both drivers not found")
        data1, data2 = ref1.to_dict(), ref2.to_dict()
        comparison = {key: (data1[key], data2[key]) for key in data1 if key != "team"}
        logger.info(f"Compared drivers {driver1} and {driver2}")
        return comparison
    except Exception as e:
        logger.error(f"Failed to compare drivers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to compare drivers: {str(e)}")

@app.get("/compare/teams/")
def compare_teams(team1: str, team2: str):
    try:
        ref1 = db.collection("teams").document(team1).get()
        ref2 = db.collection("teams").document(team2).get()
        if not ref1.exists or not ref2.exists:
            raise HTTPException(status_code=404, detail="One or both teams not found")
        data1, data2 = ref1.to_dict(), ref2.to_dict()
        comparison = {key: (data1[key], data2[key]) for key in data1}
        logger.info(f"Compared teams {team1} and {team2}")
        return comparison
    except Exception as e:
        logger.error(f"Failed to compare teams: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to compare teams: {str(e)}")