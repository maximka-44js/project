import numpy as np
import pandas as pd
from catboost import CatBoostRegressor


def get_salary_prediction(
    model_path: str,
    vacancy_id: str,
    location: str,
    schedule: str,
    experience: str,
    work_hours: float,
    skills_text: str
) -> tuple[float, float]:
    """
    Predicts salary range using CatBoost model.

    Args:
        model_path (str): Path to the CatBoost model file.
        vacancy_id (int): Vacancy ID (used as profession_id).
        location (str): Location.
        schedule (str): Work schedule.
        experience (str): Experience level.
        work_hours (float): Number of work hours.
        skills_text (str): Skills as a comma-separated string.

    Returns:
        tuple[float, float]: lowest_salary, highest_salary
    """
    # Create feature dictionary
    features = {
        "location": location,
        "schedule": schedule,
        "experience": experience,
        "work_hours": work_hours,
        "profession_id": str(vacancy_id),
        "skills_text": skills_text
    }
    
    # Load the CatBoost model
    model = CatBoostRegressor()
    model.load_model(model_path)
    
    # Convert dictionary to DataFrame format that the model expects
    X_one = pd.DataFrame([features])
    
    # Make prediction in log-scale
    y_pred_log = model.predict(X_one)  # shape: (1, 2) for MultiRMSE
    
    # Convert back from log-scale to actual salary values
    y_pred = np.expm1(y_pred_log)
    
    # Extract min and max salary from prediction
    min_salary, max_salary = y_pred[0]
    
    return float(min_salary), float(max_salary)