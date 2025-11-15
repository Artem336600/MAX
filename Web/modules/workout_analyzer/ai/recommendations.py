"""
AI-powered рекомендации по тренировкам
"""

from typing import List, Dict
from models.workout import Workout, MuscleGroup, Exercise
from analytics.stats import WorkoutStats

class WorkoutRecommendations:
    """Генерация рекомендаций на основе анализа тренировок"""
    
    @staticmethod
    def generate_recommendations(workouts: List[Workout], user_goal: str = "general") -> Dict[str, any]:
        """Генерация персональных рекомендаций"""
        
        if len(workouts) < 3:
            return {
                'recommendations': [
                    {
                        'type': 'info',
                        'title': 'Недостаточно данных',
                        'description': 'Добавьте больше тренировок для получения персональных рекомендаций'
                    }
                ]
            }
        
        recommendations = []
        
        # Анализ дисбалансов
        imbalances = WorkoutStats.detect_imbalances(workouts)
        if not imbalances['balanced']:
            for imbalance in imbalances['imbalances']:
                if imbalance['status'] == 'undertrained':
                    recommendations.append({
                        'type': 'warning',
                        'title': f'Недостаточная нагрузка: {imbalance["muscle_group"]}',
                        'description': f'Рекомендуется увеличить объем тренировок для {imbalance["muscle_group"]}',
                        'priority': 'high'
                    })
        
        # Анализ частоты
        frequency = WorkoutStats.calculate_frequency(workouts)
        for group, count in frequency.items():
            if count < 1:  # Меньше 1 раза в неделю
                recommendations.append({
                    'type': 'suggestion',
                    'title': f'Увеличьте частоту: {group}',
                    'description': f'Для лучших результатов тренируйте {group} минимум 2 раза в неделю',
                    'priority': 'medium'
                })
        
        # Анализ интенсивности
        intensity_trend = WorkoutStats.calculate_intensity_trend(workouts)
        if intensity_trend['trend'] == 'decreasing':
            recommendations.append({
                'type': 'warning',
                'title': 'Снижение интенсивности',
                'description': 'Ваша интенсивность тренировок снижается. Попробуйте увеличить нагрузку или разнообразить упражнения',
                'priority': 'high'
            })
        
        # Анализ восстановления
        recovery = WorkoutStats.calculate_recovery_time(workouts)
        for group, days in recovery.items():
            if days < 1:
                recommendations.append({
                    'type': 'warning',
                    'title': f'Недостаточное восстановление: {group}',
                    'description': f'Вы тренируете {group} слишком часто. Рекомендуется отдых минимум 48 часов',
                    'priority': 'high'
                })
            elif days > 7:
                recommendations.append({
                    'type': 'info',
                    'title': f'Длительный перерыв: {group}',
                    'description': f'Между тренировками {group} проходит {days} дней. Для поддержания формы рекомендуется тренироваться чаще',
                    'priority': 'low'
                })
        
        # Рекомендации по целям
        if user_goal == "muscle_gain":
            recommendations.append({
                'type': 'suggestion',
                'title': 'Прогрессивная перегрузка',
                'description': 'Для набора мышечной массы постепенно увеличивайте веса на 2-5% каждую неделю',
                'priority': 'medium'
            })
        elif user_goal == "strength":
            recommendations.append({
                'type': 'suggestion',
                'title': 'Силовые тренировки',
                'description': 'Фокусируйтесь на базовых упражнениях с низким количеством повторений (3-6) и высоким весом',
                'priority': 'medium'
            })
        elif user_goal == "weight_loss":
            recommendations.append({
                'type': 'suggestion',
                'title': 'Кардио и HIIT',
                'description': 'Добавьте 2-3 кардио сессии в неделю для эффективного жиросжигания',
                'priority': 'medium'
            })
        
        return {
            'total_recommendations': len(recommendations),
            'recommendations': sorted(recommendations, key=lambda x: {'high': 0, 'medium': 1, 'low': 2}[x['priority']])
        }
    
    @staticmethod
    def suggest_next_workout(workouts: List[Workout]) -> Dict[str, any]:
        """Предложить следующую тренировку на основе истории"""
        
        if not workouts:
            return {
                'suggestion': 'full_body',
                'title': 'Тренировка всего тела',
                'description': 'Начните с базовой тренировки всего тела'
            }
        
        # Анализ последних тренировок
        recent_workouts = sorted(workouts, key=lambda x: x.date, reverse=True)[:5]
        trained_groups = set()
        
        for workout in recent_workouts:
            trained_groups.update(workout.get_muscle_groups())
        
        # Найти недотренированные группы
        all_groups = set(MuscleGroup)
        untrained = all_groups - trained_groups
        
        if untrained:
            suggested_group = list(untrained)[0]
            return {
                'suggestion': suggested_group.value,
                'title': f'Тренировка {suggested_group.value}',
                'description': f'Вы давно не тренировали {suggested_group.value}. Рекомендуем сфокусироваться на этой группе',
                'exercises': WorkoutRecommendations._get_exercises_for_group(suggested_group)
            }
        
        # Если все группы тренировались, предложить самую давнюю
        recovery = WorkoutStats.calculate_recovery_time(workouts)
        if recovery:
            max_recovery_group = max(recovery.items(), key=lambda x: x[1])
            return {
                'suggestion': max_recovery_group[0],
                'title': f'Тренировка {max_recovery_group[0]}',
                'description': f'Прошло {max_recovery_group[1]} дней с последней тренировки этой группы',
                'exercises': WorkoutRecommendations._get_exercises_for_group(MuscleGroup(max_recovery_group[0]))
            }
        
        return {
            'suggestion': 'rest',
            'title': 'День отдыха',
            'description': 'Рекомендуется день отдыха для восстановления'
        }
    
    @staticmethod
    def _get_exercises_for_group(group: MuscleGroup) -> List[str]:
        """Получить рекомендуемые упражнения для мышечной группы"""
        exercises_db = {
            MuscleGroup.CHEST: ['Жим лежа', 'Отжимания', 'Жим гантелей', 'Разводка'],
            MuscleGroup.BACK: ['Подтягивания', 'Тяга штанги', 'Тяга гантели', 'Гиперэкстензия'],
            MuscleGroup.SHOULDERS: ['Жим стоя', 'Махи гантелями', 'Тяга к подбородку', 'Разводка в стороны'],
            MuscleGroup.BICEPS: ['Подъем штанги', 'Молотки', 'Концентрированный подъем'],
            MuscleGroup.TRICEPS: ['Жим узким хватом', 'Французский жим', 'Отжимания на брусьях'],
            MuscleGroup.LEGS: ['Приседания', 'Становая тяга', 'Выпады', 'Жим ногами'],
            MuscleGroup.CORE: ['Планка', 'Скручивания', 'Подъем ног', 'Русский твист'],
            MuscleGroup.CARDIO: ['Бег', 'Велосипед', 'Плавание', 'Скакалка']
        }
        
        return exercises_db.get(group, [])
