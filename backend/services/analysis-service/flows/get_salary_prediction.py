def get_salary_prediction(
    model_path: str,
    vacancy_id: int,
    location: str,
    schedule: str,
    experience: str,
    work_hours: float,
    skills_text: str
) -> tuple[float, float]:
    """
    Stub function for salary prediction.

    Args:
        vacancy_nm (str): Vacancy name.
        location (str): Location.
        schedule (str): Work schedule.
        experience (str): Experience level.
        work_hours (float): Number of work hours.
        skills_text (str): Skills as a comma-separated string.

    Returns:
        tuple[float, float]: lowest_salary, highest_salary
    """
    lowest_salary = 100000.0
    highest_salary = 2500000.0
    return lowest_salary, highest_salary