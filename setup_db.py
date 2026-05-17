"""
Script para criar as tabelas no banco MySQL online (Railway).
Execute uma vez antes do primeiro deploy:

    python setup_db.py
"""

import pymysql

DB_HOST = "junction.proxy.rlwy.net"
DB_PORT = 28109
DB_USER = "root"
DB_PASSWORD = "ZNbFieZgnaoxpjftSflcgkpzMzoUNGsU"
DB_NAME = "railway"

CREATE_SELLERS = """
CREATE TABLE IF NOT EXISTS sellers (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nome        VARCHAR(100)  NOT NULL,
    cnpj        VARCHAR(18)   NOT NULL UNIQUE,
    email       VARCHAR(120)  NOT NULL UNIQUE,
    celular     VARCHAR(20)   NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    status      VARCHAR(20)   NOT NULL DEFAULT 'Inativo',
    activation_code VARCHAR(4),
    api_token   VARCHAR(64)   UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

CREATE_PRODUCTS = """
CREATE TABLE IF NOT EXISTS products (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    seller_id   INT           NOT NULL,
    nome        VARCHAR(120)  NOT NULL,
    preco       DOUBLE        NOT NULL,
    quantidade  INT           NOT NULL DEFAULT 0,
    status      VARCHAR(20)   NOT NULL DEFAULT 'Ativo',
    imagem      VARCHAR(255),
    CONSTRAINT fk_products_seller FOREIGN KEY (seller_id) REFERENCES sellers(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

CREATE_SALES = """
CREATE TABLE IF NOT EXISTS sales (
    id                          INT AUTO_INCREMENT PRIMARY KEY,
    seller_id                   INT    NOT NULL,
    product_id                  INT    NOT NULL,
    quantidade_vendida          INT    NOT NULL,
    preco_produto_momento_venda DOUBLE NOT NULL,
    created_at                  DATETIME,
    CONSTRAINT fk_sales_seller  FOREIGN KEY (seller_id)  REFERENCES sellers(id),
    CONSTRAINT fk_sales_product FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""


def main():
    print(f"Conectando em {DB_HOST}:{DB_PORT} / {DB_NAME} ...")
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
    )

    try:
        with conn.cursor() as cursor:
            print("Criando tabela 'sellers' ...")
            cursor.execute(CREATE_SELLERS)

            print("Criando tabela 'products' ...")
            cursor.execute(CREATE_PRODUCTS)

            print("Criando tabela 'sales' ...")
            cursor.execute(CREATE_SALES)

        conn.commit()
        print("\nTabelas criadas com sucesso!")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
