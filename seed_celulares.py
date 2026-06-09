import sqlite3
import random
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "mercadinho.db")

DDDs = ["11", "21", "31", "41", "51", "61", "71", "81", "85", "91"]

def gerar_celular():
    ddd = random.choice(DDDs)
    parte1 = random.randint(9000, 9999)
    parte2 = random.randint(1000, 9999)
    return f"({ddd}) {parte1}-{parte2}"

def main():
    print(f"Conectando em {DB_PATH} ...")
    conn = sqlite3.connect(DB_PATH)

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, celular FROM sellers")
        sellers = cursor.fetchall()

        if not sellers:
            print("Nenhum seller encontrado.")
            return

        print(f"\n{len(sellers)} seller(s) encontrado(s):\n")

        for seller_id, nome, celular_atual in sellers:
            novo_celular = gerar_celular()
            cursor.execute(
                "UPDATE sellers SET celular = ? WHERE id = ?",
                (novo_celular, seller_id)
            )
            print(f"  [{seller_id}] {nome}: {celular_atual} → {novo_celular}")

        conn.commit()
        print("\nCelulares atualizados com sucesso!")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
