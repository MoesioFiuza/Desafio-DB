from fastapi.testclient import TestClient


def test_post_documento_201_envelope(client: TestClient) -> None:
    payload = {
        "titulo": "Doc API",
        "autor": "Autor",
        "conteudo": "Conteudo com informacao util.",
        "data": "2025-06-01",
        "latitude": -30.0,
        "longitude": -51.0,
    }
    res = client.post("/documentos", json=payload)
    assert res.status_code == 201
    body = res.json()
    assert body["success"] is True
    assert body["message"] == "Documento criado com sucesso."
    assert body["trace_id"]
    assert body["data"]["titulo"] == "Doc API"
    assert body["data"]["latitude"] == -30.0
    assert res.headers.get("request-id")


def test_get_palavra_chave_returns_match(client: TestClient) -> None:
    client.post(
        "/documentos",
        json={
            "titulo": "T1",
            "autor": "A1",
            "conteudo": "Texto unico com token informacao",
            "data": "2025-01-01",
            "latitude": -30.0,
            "longitude": -51.0,
        },
    )
    r = client.get("/documentos", params={"palavraChave": "informacao"})
    assert r.status_code == 200
    assert r.json()["message"] == "Foi encontrado 1 documento."
    data = r.json()["data"]
    assert len(data) == 1
    assert data[0]["score"] is not None


def test_get_both_palavra_chave_e_busca_400(client: TestClient) -> None:
    r = client.get(
        "/documentos",
        params={"palavraChave": "a", "busca": "b"},
    )
    assert r.status_code == 400
    assert r.json()["success"] is False
    assert r.json()["code"]


def test_get_neither_search_params_400(client: TestClient) -> None:
    r = client.get("/documentos")
    assert r.status_code == 400
    body = r.json()
    assert body["success"] is False
    assert body["code"] == "domain_validation_error"
    assert "exatamente um" in body["message"]
    assert body["trace_id"]


def test_get_busca_sem_resultados_mensagem_amigavel(client: TestClient) -> None:
    r = client.get("/documentos", params={"palavraChave": "xyz_token_inexistente_123"})
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["data"] == []
    assert body["message"] == "Nenhum documento foi encontrado com os filtros informados."


def test_get_offset_and_limit(client: TestClient) -> None:
    for i in range(3):
        client.post(
            "/documentos",
            json={
                "titulo": f"D{i}",
                "autor": "A",
                "conteudo": "palavra repetida teste",
                "data": "2025-01-01",
                "latitude": -30.0,
                "longitude": -51.0,
            },
        )
    first_page = client.get(
        "/documentos",
        params={"palavraChave": "teste", "limit": 2, "offset": 0},
    )
    assert first_page.status_code == 200
    assert first_page.json()["message"] == "Foram encontrados 2 documentos."
    first_ids = [item["id"] for item in first_page.json()["data"]]

    r = client.get("/documentos", params={"palavraChave": "teste", "limit": 2, "offset": 1})
    assert r.status_code == 200
    assert r.json()["message"] == "Foram encontrados 2 documentos."
    second_page = r.json()["data"]
    assert len(second_page) == 2
    second_ids = [item["id"] for item in second_page]
    assert second_ids[0] == first_ids[1]


def test_conteudo_preview_query(client: TestClient) -> None:
    client.post(
        "/documentos",
        json={
            "titulo": "T",
            "autor": "A",
            "conteudo": "ABCDEFGHIJ",
            "data": "2025-01-01",
            "latitude": 0.0,
            "longitude": 0.0,
        },
    )
    r = client.get(
        "/documentos",
        params={"palavraChave": "ABC", "conteudoPreview": 5},
    )
    assert r.status_code == 200
    assert r.json()["data"][0]["conteudo"].endswith("...")


def test_validation_extra_field_forbidden(client: TestClient) -> None:
    res = client.post(
        "/documentos",
        json={
            "titulo": "T",
            "autor": "A",
            "conteudo": "C",
            "data": "2025-01-01",
            "latitude": 0.0,
            "longitude": 0.0,
            "extra": 1,
        },
    )
    assert res.status_code == 422
    body = res.json()
    assert body["success"] is False
    assert body["code"] == "request_validation_error"
    assert "não é permitido" in body["message"]
