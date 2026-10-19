import os
from sqlalchemy import text
from app.config.database import SessionLocal

def update_uf():
    print("Atualizando siglas de UF para registros existentes do CAR...")
    db = SessionLocal()
    try:
        # Extrai os 2 primeiros caracteres do codigo_imovel (Padrão SFB)
        sql = text("UPDATE car_propriedades SET sigla_uf = LEFT(codigo_imovel, 2) WHERE sigla_uf IS NULL")
        result = db.execute(sql)
        db.commit()
        print(f"Sucesso! Registros atualizados: {result.rowcount}")
    except Exception as e:
        print(f"Erro ao atualizar UF: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_uf()
