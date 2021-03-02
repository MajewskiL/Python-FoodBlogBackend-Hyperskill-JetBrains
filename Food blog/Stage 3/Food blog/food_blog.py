import sqlite3
import sys
data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
        "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
        "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}


def create_tables(database):
    conn = sqlite3.connect(database)
    convoy = conn.cursor()
    convoy.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    convoy.execute(f"CREATE TABLE IF NOT EXISTS ingredients(ingredient_id INTEGER PRIMARY KEY, ingredient_name TEXT NOT NULL UNIQUE);")
    convoy.execute(f"CREATE TABLE IF NOT EXISTS measures(measure_id INTEGER PRIMARY KEY, measure_name TEXT UNIQUE);")
    convoy.execute(f"CREATE TABLE IF NOT EXISTS meals(meal_id INTEGER PRIMARY KEY, meal_name TEXT NOT NULL UNIQUE);")
    convoy.execute(f"CREATE TABLE IF NOT EXISTS recipes(recipe_id INTEGER PRIMARY KEY, recipe_name TEXT NOT NULL, recipe_description TEXT);")
    convoy.execute(f"CREATE TABLE IF NOT EXISTS serve(serve_id INTEGER PRIMARY KEY, recipe_id INTEGER NOT NULL, meal_id INTEGER NOT NULL, "
                   f"FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id), FOREIGN KEY(meal_id) REFERENCES meals(meal_id));")
    conn.commit()
    for table in data:
        for item in data[table]:
            try:
                convoy.execute(f"INSERT INTO {table}({table[:-1]}_name) VALUES('{item}')")
            except sqlite3.IntegrityError:
                pass
    conn.commit()
    conn.close()


def feeding_database(database):
    conn = sqlite3.connect(database)
    convoy = conn.cursor()
    while True:
        print("Pass the empty recipe name to exit.")
        name = input("Recipe name: ")
        if name == "":
            return
        description = input('Recipe description: ')
        recipe_id = convoy.execute(f"INSERT INTO recipes(recipe_name, recipe_description) VALUES('{name}', '{description}')").lastrowid
        conn.commit()
        meals_data = convoy.execute(f"SELECT * FROM meals")
        print(" ".join([str(measure[0]) + ") " + measure[1] + " " for measure in meals_data.fetchall()]))
        meals = input("When the dish can be served: ").split(" ")
        for meal in meals:
            convoy.execute(f"INSERT INTO serve(meal_id, recipe_id) VALUES('{meal}', '{recipe_id}')")
        conn.commit()


create_tables(sys.argv[1])
feeding_database(sys.argv[1])
