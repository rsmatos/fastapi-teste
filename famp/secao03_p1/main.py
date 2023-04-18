from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException, status, Response, Path, Header, Depends
from time import sleep

from models import Curso, cursos


def fake_db():
    try:
        print("Abrindo conexão com o banco de dados...")
        # sleep(1)
    finally:
        print("Fechando conexão com o banco de dados...")
        # sleep(1)


app = FastAPI(title="API de Cursos do Rafael", version="0.0.1", description="Uma API para estudo do FastAPI")


@app.get("/cursos", description="Retorna todos os cursos ou uma lista vazia.", summary="Retorna todos os cursos",
         response_model=List[Curso],
         response_description="Cursos encontrados com sucesso.")
async def get_cursos(db: Any = Depends(fake_db)):
    return cursos


@app.get("/curso/{curso_id}", description="Retorna um curso referente ao ID fornecido",
         summary="Retorna um curso específico", response_model=Curso)
async def get_curso(
        curso_id: int = Path(default=None, title="ID do curso", description="Deve ser entre 1 e 2", gt=0, lt=3),
        db: Any = Depends(fake_db)):
    try:
        curso = cursos[curso_id]
        return curso
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado.")


@app.post("/cursos", status_code=status.HTTP_201_CREATED, description="Adiciona um curso", summary="Adiciona um curso",
          response_model=Curso)
async def post_curso(curso: Curso, db: Any = Depends(fake_db)):
    curso.id = len(cursos)
    cursos.append(curso)
    return curso


@app.put("/cursos/{curso_id}", description="Altera um curso de acordo com o ID informado",
         summary="Altera um curso específico", response_model=Curso)
async def put_curso(curso_id: int, curso: Curso, db: Any = Depends(fake_db)):
    print(cursos)
    for cs in cursos:
        if curso_id == cs.id:
            curso.id = curso_id
            cursos.insert(curso_id, curso)
            return curso
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Não existe um curso com o id {curso_id}.")


@app.delete("/cursos/{curso_id}", description="Remove um curso de acordo com o ID informado",
            summary="Remove um curso em específico")
async def delete_curso(curso_id: int, db: Any = Depends(fake_db)):
    for cs in cursos:
        if curso_id == cs.id:
            del cursos[curso_id]
            return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Não existe um curso com o id {curso_id}.")


@app.post("/curso/{id}")
async def inser_curso_by_id(id: int, curso: Curso):
    for cs in cursos:
        if id == cs.id:
            print("tem")
            return

    print("inseriu")
    curso.id = id
    cursos.insert(id, curso)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug", reload=True)
