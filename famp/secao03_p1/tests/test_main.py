import sys
import json
import random

import requests as client
from fastapi import status
from pytest import mark

from models import Curso

CURSOS_URI = "/cursos"

sys.path.insert(0, "../")


class TestClass:
    request_url = "http://localhost:8000"

    @mark.get
    def test_should_return_cursos_when_acessing_uri_cursos(self):
        response = client.get(url=self.request_url + CURSOS_URI)

        cursos = [
            Curso(id=1, titulo="Algoritmos e Lógica de Programação", aulas=87, horas=67),
        ]

        response_as_list = json.loads(response.text)
        print(response_as_list)
        for curso in cursos:
            assert curso in response_as_list

    @mark.get
    def test_should_return_status_code_not_found_and_curso_not_found(self):
        response = client.get(url=self.request_url + "/curso/999999999999")

        assert status.HTTP_422_UNPROCESSABLE_ENTITY == response.status_code
        print(response.text)

    @mark.post
    def test_should_insert_a_new_curso(self):
        curso = self.create_random_curso()

        response = client.post(url=self.request_url + CURSOS_URI, data=json.dumps(curso.dict()))

        assert status.HTTP_201_CREATED == response.status_code

    @mark.put
    def test_should_update_curso(self):
        curso = self.create_random_curso()
        response = client.put(url=self.request_url + CURSOS_URI + "/1", data=json.dumps(curso.dict()))
        curso.id = 1
        assert status.HTTP_200_OK == response.status_code
        assert curso == json.loads(response.text)

    @mark.put
    def test_put_request_should_return_404_when_sending_wrong_id(self):
        curso = self.create_random_curso()
        curso_id = "99999999999999"
        response = client.put(url=self.request_url + CURSOS_URI + f"/{curso_id}", data=json.dumps(curso.dict()))

        assert status.HTTP_404_NOT_FOUND == response.status_code
        assert {"detail": f"Não existe um curso com o id {curso_id}."} == json.loads(response.text)

    @mark.delete
    def test_delete_request_should_retun_200(self):
        curso = self.create_random_curso()
        client.post(url=self.request_url + "/curso/1", data=json.dumps(curso.dict()))

        curso_id = "1"
        response = client.delete(url=self.request_url + CURSOS_URI + f"/{curso_id}")
        client.post(url=self.request_url + "/curso/1", data=json.dumps(curso.dict()))

        assert status.HTTP_204_NO_CONTENT == response.status_code

    def create_random_curso(self):
        return Curso(titulo="Teste Alo " + str(random.randrange(10, 200)), aulas=random.randrange(10, 200),
                     horas=random.randrange(10, 200))
