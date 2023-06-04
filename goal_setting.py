# goal_setting.py
def set_clear_goals():
    goals = []
    print("Define roles for the AI system.\n")

    while True:
        goal = input("Add another role (or press enter to finish): ")
        if not goal:
            break

        goals.append(goal)

    return goals