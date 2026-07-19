# def test_cors_blocks_frontend_origin() -> None:
#     client = TestClient(app)
#     response = client.get("/docs", headers={"origin": "http://localhost:5173"})

#     assert response.status_code == 200
#     assert "access-control-allow-origin" not in response.headers
