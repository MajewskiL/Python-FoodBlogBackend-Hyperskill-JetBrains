import sqlite3
import sys

data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
        "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
        "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}
wsad = ("Milkshake\nBlend all ingredients and put in the fridge.\n1 3 4\n500 ml milk\n1 cup strawberry\n1 tbsp sugar\n", \
        "\n",
        "Hot cacao\nPour the ingredients into the hot milk. Mix it up.\n1 4\n250 ml milk\n2 tbsp cacao\n1 tsp sugar\n",
        "\n",
        "Fruit salad\nCut strawberries and mix with other fruits. you can sprinkle everything with sugar.\n3 4\n100 g strawberry\n50 g black\n1 cup blue\n1 tsp sugar\n",
        "\n",
        "\n")

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
    convoy.execute(f"CREATE TABLE IF NOT EXISTS quantity(quantity_id INTEGER PRIMARY KEY, recipe_id INTEGER NOT NULL, quantity INTEGER NOT NULL, measure_id INTEGER NOT NULL, ingredient_id INTEGER NOT NULL, "
                   f"FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id), FOREIGN KEY(measure_id) REFERENCES measures(measure_id), FOREIGN KEY(ingredient_id) REFERENCES ingredients(ingredient_id));")

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
        meals = input("Enter proposed meals separated by a space: ").split(" ")
        for meal in meals:
            convoy.execute(f"INSERT INTO serve(meal_id, recipe_id) VALUES('{meal}', '{recipe_id}')")
        conn.commit()
        while True:
            ingredient = input("Input quantity of ingredient <press enter to stop>: ").split(" ")
            try:
                if ingredient[0] != "":
                    ingredient[0] = int(ingredient[0])
            except ValueError:
                print("Quantity should be an integer.")
            else:
                if ingredient[0] == "":
                    conn.commit()
                    break
                elif any([len(ingredient) < 2, len(ingredient) > 3]):
                    print("Wrong form! Should be [quantity <measure> ingredient]!")
                elif not isinstance(ingredient[0], int):
                    print("Quantity should be an integer.")
                else:
                    if len(ingredient) == 2:
                        i_measure = convoy.execute(f"SELECT measure_id FROM measures WHERE measure_name = ''").fetchall()
                        i_ingredient = convoy.execute(f"SELECT ingredient_id FROM ingredients WHERE ingredient_name LIKE '%{ingredient[1]}%'").fetchall()
                    else:
                        i_measure = convoy.execute(f"SELECT measure_id FROM measures WHERE measure_name LIKE '{ingredient[1]}%'").fetchall()
                        i_ingredient = convoy.execute(f"SELECT ingredient_id FROM ingredients WHERE ingredient_name LIKE '%{ingredient[2]}%'").fetchall()
                    if any([len(i_measure) !=1, len(i_ingredient) != 1]):
                        if len(i_measure) == 0:
                            print("There is no such a measure!")
                        elif len(i_measure) !=1:
                            print("The measure is not conclusive!")
                        if len(i_ingredient) == 0:
                            print("There is no such a ingredient!")
                        elif len(i_ingredient) !=1:
                            print("The ingredient is not conclusive!")
                    else:
                        convoy.execute(f"INSERT INTO quantity(recipe_id, quantity, measure_id, ingredient_id) VALUES('{recipe_id}', '{ingredient[0]}', '{i_measure[0][0]}','{i_ingredient[0][0]}')")


create_tables(sys.argv[1])
feeding_database(sys.argv[1])
