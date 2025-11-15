"""
Статистический анализ тренировок
"""

from typing import List, Dict
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict

from models.workout import Workout, MuscleGroup

class WorkoutStats:
    """Класс для расчета статистики тренировок"""
    
    @staticmethod
    def calculate_weekly_volume(workouts: List[Workout]) -> Dict[str, float]:
        """Недельный объем по мышечным группам"""
        volume_by_group = defaultdict(float)
        
        for workout in workouts:
            for exercise in workout.exercises:
                if exercise.weight:
                    volume = exercise.sets * exercise.reps * exercise.weight
                    for group in exercise.muscle_groups:
                        volume_by_group[group.value] += volume
        
        return dict(volume_by_group)
    
    @staticmethod
    def calculate_frequency(workouts: List[Workout]) -> Dict[str, int]:
        """Частота тренировок по мышечным группам"""
        frequency = defaultdict(int)
        
        for workout in workouts:
            groups = workout.get_muscle_groups()
            for group in groups:
                frequency[group.value] += 1
        
        return dict(frequency)
    
    @staticmethod
    def calculate_progress(workouts: List[Workout], exercise_name: str) -> Dict[str, any]:
        """Прогресс по конкретному упражнению"""
        exercise_data = []
        
        for workout in workouts:
            for ex in workout.exercises:
                if ex.name.lower() == exercise_name.lower():
                    exercise_data.append({
                        'date': workout.date,
                        'weight': ex.weight or 0,
                        'reps': ex.reps,
                        'volume': (ex.weight or 0) * ex.reps * ex.sets
                    })
        
        if not exercise_data:
            return {
                'found': False,
                'message': f'Упражнение "{exercise_name}" не найдено'
            }
        
        # Сортировка по дате
        exercise_data.sort(key=lambda x: x['date'])
        
        # Расчет прогресса
        first = exercise_data[0]
        last = exercise_data[-1]
        
        weight_progress = ((last['weight'] - first['weight']) / first['weight'] * 100) if first['weight'] > 0 else 0
        volume_progress = ((last['volume'] - first['volume']) / first['volume'] * 100) if first['volume'] > 0 else 0
        
        return {
            'found': True,
            'exercise_name': exercise_name,
            'total_workouts': len(exercise_data),
            'first_workout': {
                'date': first['date'].isoformat(),
                'weight': first['weight'],
                'reps': first['reps']
            },
            'last_workout': {
                'date': last['date'].isoformat(),
                'weight': last['weight'],
                'reps': last['reps']
            },
            'weight_progress_percent': round(weight_progress, 1),
            'volume_progress_percent': round(volume_progress, 1),
            'data_points': exercise_data
        }
    
    @staticmethod
    def calculate_intensity_trend(workouts: List[Workout]) -> Dict[str, any]:
        """Тренд интенсивности тренировок"""
        if len(workouts) < 2:
            return {'trend': 'insufficient_data'}
        
        intensities = [w.intensity for w in sorted(workouts, key=lambda x: x.date)]
        
        # Линейная регрессия
        x = np.arange(len(intensities))
        coefficients = np.polyfit(x, intensities, 1)
        slope = coefficients[0]
        
        avg_intensity = np.mean(intensities)
        
        if slope > 0.1:
            trend = 'increasing'
        elif slope < -0.1:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'slope': round(slope, 3),
            'average_intensity': round(avg_intensity, 2),
            'current_intensity': round(intensities[-1], 2)
        }
    
    @staticmethod
    def calculate_recovery_time(workouts: List[Workout]) -> Dict[MuscleGroup, float]:
        """Среднее время восстановления между тренировками мышечных групп"""
        last_workout = defaultdict(lambda: None)
        recovery_times = defaultdict(list)
        
        sorted_workouts = sorted(workouts, key=lambda x: x.date)
        
        for workout in sorted_workouts:
            groups = workout.get_muscle_groups()
            for group in groups:
                if last_workout[group]:
                    days = (workout.date - last_workout[group]).days
                    recovery_times[group].append(days)
                last_workout[group] = workout.date
        
        avg_recovery = {}
        for group, times in recovery_times.items():
            if times:
                avg_recovery[group.value] = round(np.mean(times), 1)
        
        return avg_recovery
    
    @staticmethod
    def detect_imbalances(workouts: List[Workout]) -> Dict[str, any]:
        """Обнаружение дисбалансов в тренировках"""
        volume_by_group = WorkoutStats.calculate_weekly_volume(workouts)
        
        if not volume_by_group:
            return {'balanced': True, 'imbalances': []}
        
        avg_volume = np.mean(list(volume_by_group.values()))
        imbalances = []
        
        for group, volume in volume_by_group.items():
            deviation = ((volume - avg_volume) / avg_volume * 100) if avg_volume > 0 else 0
            
            if deviation < -30:
                imbalances.append({
                    'muscle_group': group,
                    'status': 'undertrained',
                    'deviation_percent': round(deviation, 1)
                })
            elif deviation > 30:
                imbalances.append({
                    'muscle_group': group,
                    'status': 'overtrained',
                    'deviation_percent': round(deviation, 1)
                })
        
        return {
            'balanced': len(imbalances) == 0,
            'imbalances': imbalances,
            'volume_distribution': volume_by_group
        }
