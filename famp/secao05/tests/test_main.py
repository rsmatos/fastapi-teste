import json
import random
import requests as client
from fastapi import status
from models.curso_model import CursoModel

CURSOS_URI = "/cursos"
URL = "http://localhost:8000/api/v1"


class TestClass:

    def test_should_do_crud_operations_with_curso(self):
        # Cria e valida curso 1
        curso = self.create_curso()
        self.post_and_validate_curso(curso)

        # Cria e valida curso 2
        curso2 = self.create_curso()
        self.post_and_validate_curso(curso2)

        # Pega todos os cursos criados, esperado que sejam 2
        response = client.get(URL + CURSOS_URI)
        assert status.HTTP_200_OK == response.status_code
        assert len(json.loads(response.text)) == 2

        cursos = json.loads(response.text)
        print(cursos)
        # Pega curso de ID
        curso_id = str(cursos[0]["id"])
        response = client.get(URL + CURSOS_URI + "/" + curso_id)
        assert status.HTTP_200_OK == response.status_code

        # Muda curso de ID
        curso_updated = self.create_curso()
        response = client.put(URL + CURSOS_URI + "/" + curso_id, data=curso_updated.json())
        assert status.HTTP_202_ACCEPTED == response.status_code
        self.validate_curso(curso_updated, response.text)

        # Pega todos os cursos criados + mudados, esperado que sejam 2
        response = client.get(URL + CURSOS_URI)
        assert status.HTTP_200_OK == response.status_code
        cursos = json.loads(response.text)
        assert len(cursos) > 0

        # Deleta curso de ID
        response = client.delete(URL + CURSOS_URI + "/" + str(cursos[0]["id"]))
        assert status.HTTP_204_NO_CONTENT == response.status_code

        # Tenta pegar curso de ID == 1, porém deve not found
        response = client.get(URL + CURSOS_URI + "/" + str(cursos[0]["id"]))
        assert status.HTTP_404_NOT_FOUND == response.status_code

        # Pega todos os cursos criados + mudados, esperado que seja 1
        response = client.get(URL + CURSOS_URI)
        assert status.HTTP_200_OK == response.status_code
        cursos_new = json.loads(response.text)
        assert len(cursos) - len(cursos_new) == 1

        # Pega curso de ID
        response = client.get(URL + CURSOS_URI + "/" + str(cursos[1]["id"]))
        assert status.HTTP_200_OK == response.status_code
        print(curso2)
        print(cursos)
        self.validate_curso(curso2, response.text)

    def setup_method(self):
        self.clear_database()

    def teardown_method(self):
        self.clear_database()

    def clear_database(self):
        response = client.get(URL + CURSOS_URI)
        assert status.HTTP_200_OK == response.status_code
        cursos = json.loads(response.text)
        for cs in cursos:
            # Deleta curso de ID
            response = client.delete(URL + CURSOS_URI + "/" + str(cs["id"]))
            assert status.HTTP_204_NO_CONTENT == response.status_code

    def post_and_validate_curso(self, curso):
        response = client.post(url=URL + CURSOS_URI, data=curso.json())
        assert status.HTTP_201_CREATED == response.status_code
        self.validate_curso(curso, response.text)

    def validate_curso(self, curso, response_text):
        curso_response = json.loads(response_text)
        assert curso.titulo == curso_response["titulo"]
        assert curso.aulas == curso_response["aulas"]
        assert curso.horas == curso_response["horas"]

    def create_curso(self):
        return CursoModel(titulo=f"Testando 123 testando {random.randrange(0, 100)}", aulas=random.randrange(10, 300),
                           horas=random.randrange(10, 300))
