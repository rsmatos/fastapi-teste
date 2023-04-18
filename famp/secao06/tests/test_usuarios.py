import json
import requests as client
from fastapi import status
from schemas.usuario_schema import UsuarioSchemaBase, UsuarioSchemaArtigos, UsuarioSchemaCreate, UsuarioSchemaUpdate

URL = "http://localhost:8000/api/v1/usuarios/"


class TestUsuarioApi:

    def setup_method(self):
        self.clear_database()

    def teardown_method(self):
        self.clear_database()

    def test_should_execute_crud_for_user(self):
        usuario1: UsuarioSchemaCreate = UsuarioSchemaCreate(nome="Rafael", sobrenome="Soares",
                                                            email="rmatos@cpqd.com.br",
                                                            senha="12345",
                                                            eh_admin=True)

        response = client.post(URL + "signup", data=usuario1.json())
        assert status.HTTP_201_CREATED == response.status_code

        response = client.post(URL + "signup", data=usuario1.json())
        assert status.HTTP_406_NOT_ACCEPTABLE == response.status_code

        usuario2: UsuarioSchemaCreate = UsuarioSchemaCreate(nome="Rafael", sobrenome="Soares",
                                                            email="rafael.soaresmat@gmail.com",
                                                            senha="12345",
                                                            eh_admin=False)

        response = client.post(URL + "signup", data=usuario2.json())
        assert status.HTTP_201_CREATED == response.status_code

        response = client.post(URL + "signup", data=usuario2.json())
        assert status.HTTP_406_NOT_ACCEPTABLE == response.status_code

        form_data = {"username": usuario1.email,
                     "password": usuario1.senha,
                     "scope": "",
                     "client_id": "",
                     "client_secret": "",
                     "gran_type": "password"}

        response = client.post(URL + "login",
                               data=form_data)
        print(response.text)
        assert response.status_code == status.HTTP_200_OK
        token_response = json.loads(response.text)
        assert token_response["access_token"]
        assert token_response["token_type"] == "bearer"

        response = client.get(URL + "logado", headers={
            "Authorization": token_response["token_type"] + " " + token_response["access_token"]})
        assert response.status_code == status.HTTP_200_OK
        usuario_logado = UsuarioSchemaBase(**json.loads(response.text))
        assert usuario_logado.email == usuario1.email

        response = client.get(URL)
        assert status.HTTP_200_OK == response.status_code
        usuarios = json.loads(response.text)
        assert len(usuarios) == 2

        response = client.get(URL + str(usuarios[0]["id"]))
        usuario1_salvo = UsuarioSchemaBase(**json.loads(response.text))
        self.confere_campos_do_usuario(usuario1, usuario1_salvo)

        usuario2_updated = UsuarioSchemaUpdate(nome="Thalia", sobrenome="Cardoso", email="thaliacardoso@gmail.com",
                                               eh_admin=True, senha="123")
        response = client.put(URL + str(usuarios[1]["id"]), data=usuario2_updated.json())
        assert status.HTTP_202_ACCEPTED == response.status_code
        usuario2_salvo_updated = UsuarioSchemaBase(**json.loads(response.text))
        self.confere_campos_do_usuario(usuario2_updated, usuario2_salvo_updated)

        response = client.get(URL)
        assert status.HTTP_200_OK == response.status_code
        usuarios_updated = json.loads(response.text)

        response = client.delete(URL + str(usuarios_updated[1]["id"]))
        assert status.HTTP_204_NO_CONTENT == response.status_code

    def confere_campos_do_usuario(self, usuario, usuario_salvo):
        assert usuario_salvo.nome == usuario.nome
        assert usuario_salvo.sobrenome == usuario.sobrenome
        assert usuario_salvo.email == usuario.email
        assert usuario_salvo.eh_admin == usuario.eh_admin

    def clear_database(self):
        response = client.get(URL)
        usuarios = json.loads(response.text)

        for usuario in usuarios:
            response = client.delete(URL + str(usuario["id"]))
            assert status.HTTP_204_NO_CONTENT == response.status_code
