import json
import requests as client
from fastapi import status
from schemas.usuario_schema import UsuarioSchemaBase, UsuarioSchemaCreate
from schemas.artigo_schema import ArtigoSchema

URL = "http://localhost:8000/api/v1/artigos/"
URL_USUARIO = "http://localhost:8000/api/v1/usuarios/"


class TestArtigos:
    usuario_id: str
    email: str
    senha: str
    token: str

    def setup_method(self):
        try:
            self.clear_database()
        finally:
            self.cria_usuario()
            self.faz_login()

    def test_should_do_crud_operations_for_artigos(self):
        artigo1: ArtigoSchema = ArtigoSchema(titulo="teste1", descricao="artigo teste1",
                                             url_fonte="https://fastapi.tiangolo.com/pt/async/")
        artigo1_inserido = self.cria_artigo(artigo1)
        self.valida_campos_dos_artigos(artigo1, artigo1_inserido)

        artigo2: ArtigoSchema = ArtigoSchema(titulo="teste2", descricao="artigo teste2",
                                             url_fonte="https://medium.com/@viniciuschan/solid-com-python-entendendo-os-5-princ%C3%ADpios-na-pr%C3%A1tica-f2af330b7751")
        artigo2_inserido = self.cria_artigo(artigo2)
        self.valida_campos_dos_artigos(artigo2, artigo2_inserido)

        response = client.get(URL)
        assert response.status_code == status.HTTP_200_OK
        artigos = json.loads(response.text)
        assert len(artigos) == 2

        response = client.get(URL + str(artigo1_inserido.id))
        assert response.status_code == status.HTTP_200_OK
        self.valida_campos_dos_artigos(artigo1_inserido, ArtigoSchema(**json.loads(response.text)))

        artigo2_updated: ArtigoSchema = ArtigoSchema(titulo="teste225345635", descricao="artigo teste2",
                                                     url_fonte="https://medium.com/@viniciuschan/solid-com-python-entendendo-os-5-princ%C3%ADpios-na-pr%C3%A1tica-f2af330b7751")
        response = client.put(URL + str(artigo2_inserido.id), data=artigo2_updated.json(),
                              headers={"Authorization": self.token})
        assert response.status_code == status.HTTP_202_ACCEPTED
        self.valida_campos_dos_artigos(artigo2_updated, ArtigoSchema(**json.loads(response.text)))
        artigo2_updated = ArtigoSchema(**json.loads(response.text))

        response = client.delete(URL + str(artigo2_updated.id), headers={"Authorization": self.token})
        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = client.get(URL)
        assert response.status_code == status.HTTP_200_OK
        artigos = json.loads(response.text)
        assert len(artigos) == 1

    def cria_artigo(self, artigo) -> ArtigoSchema:
        response = client.post(URL, data=artigo.json(), headers={"Authorization": self.token})
        assert response.status_code == status.HTTP_201_CREATED
        return ArtigoSchema(**json.loads(response.text))

    def valida_campos_dos_artigos(self, artigo, artigo_retornado):
        assert artigo_retornado.titulo == artigo.titulo
        assert artigo_retornado.url_fonte == artigo.url_fonte
        assert artigo_retornado.descricao == artigo.descricao

    def teardown_method(self):
        self.clear_database()

    def clear_database(self):
        response = client.get(URL_USUARIO)
        usuarios = json.loads(response.text)

        for usuario in usuarios:
            response = client.delete(URL_USUARIO + str(usuario["id"]))
            assert status.HTTP_204_NO_CONTENT == response.status_code

        response = client.get(URL)
        assert len(json.loads(response.text)) == 0

    def cria_usuario(self):
        usuario: UsuarioSchemaCreate = UsuarioSchemaCreate(nome="Rafael", sobrenome="Soares",
                                                           email="rmatos@cpqd.com.br",
                                                           senha="12345",
                                                           eh_admin=True)
        response = client.post(URL_USUARIO + "signup", data=usuario.json())
        assert response.status_code == status.HTTP_201_CREATED
        usuario_criado = UsuarioSchemaBase(**json.loads(response.text))
        self.usuario_id = usuario_criado.id
        self.email = usuario.email
        self.senha = usuario.senha

    def faz_login(self):
        form_data = {"username": self.email,
                     "password": self.senha,
                     "scope": "",
                     "client_id": "",
                     "client_secret": "",
                     "gran_type": "password"}

        response = client.post(URL_USUARIO + "login",
                               data=form_data)
        assert response.status_code == status.HTTP_200_OK
        token_response = json.loads(response.text)
        assert token_response["access_token"]
        assert token_response["token_type"] == "bearer"
        self.token = token_response["token_type"] + " " + token_response["access_token"]
