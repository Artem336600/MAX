"""
Модели данных для тренировок
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class MuscleGroup(str, Enum):
    CHEST = "chest"
    BACK = "back"
    SHOULDERS = "shoulders"
    BICEPS = "biceps"
    TRICEPS = "triceps"
    LEGS = "legs"
    CORE = "core"
    CARDIO = "cardio"

class ExerciseType(str, Enum):
    STRENGTH = "strength"
    CARDIO = "cardio"
    FLEXIBILITY = "flexibility"
    BALANCE = "balance"

class Exercise(BaseModel):
    name: str
    type: ExerciseType
    muscle_groups: List[MuscleGroup]
    sets: int
    reps: int
    weight: Optional[float] = None  # кг
    duration: Optional[int] = None  # секунды
    distance: Optional[float] = None  # км
    calories: Optional[int] = None
    notes: Optional[str] = None

class Workout(BaseModel):
    id: Optional[str] = None
    user_id: str
    date: datetime
    title: str
    exercises: List[Exercise]
    duration: int  # минуты
    total_calories: int
    intensity: float  # 0-10
    notes: Optional[str] = None
    
    def calculate_volume(self) -> float:
        """Общий объем тренировки (sets * reps * weight)"""
        volume = 0
        for ex in self.exercises:
            if ex.weight:
                volume += ex.sets * ex.reps * ex.weight
        return volume
    
    def get_muscle_groups(self) -> List[MuscleGroup]:
        """Получить все задействованные мышечные группы"""
        groups = set()
        for ex in self.exercises:
            groups.update(ex.muscle_groups)
        return list(groups)

class WorkoutProgram(BaseModel):
    """Тренировочная программа"""
    id: Optional[str] = None
    user_id: str
    name: str
    description: str
    duration_weeks: int
    workouts_per_week: int
    goal: str  # strength, endurance, weight_loss, muscle_gain
    exercises: List[Exercise]
