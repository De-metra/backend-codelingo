import pytest

# GET /courses/
@pytest.mark.asyncio
async def test_get_all_courses(client):
    response = await client.get("/api/courses/")

    assert response.status_code == 200

# GET /courses/{id}
@pytest.mark.asyncio
async def test_get_courses_with_no_levels(client, created_course):
    response = await client.get(f"/api/courses/{created_course.id}/")

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_courses_levels_incorrect_id(client):
    response = await client.get("/api/courses/22/")

    assert response.status_code == 404

# GET /courses/{id}/levels
# @pytest.mark.asyncio
# async def test_get_levels_with_progress(client, auth_header, created_course):
#     response = await client.get(f"/api/courses/{created_course.id}/levels", headers=auth_header)

#     assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_courses_levels_with_progress(client, auth_header, created_course):
    response = await client.get(f"/api/courses/{created_course.id}/levels", headers=auth_header)

    assert response.status_code == 404

# POST /courses/{id}/start
@pytest.mark.asyncio
async def test_start_course(client, auth_header, created_course):
    response = await client.post(f"/api/courses/{created_course.id}/start", headers=auth_header)

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_start_course_incorrect_id(client, auth_header):
    response = await client.post(f"/api/courses/22/start", headers=auth_header)

    assert response.status_code == 404

@pytest.mark.asyncio
async def test_start_course_already_started(client, auth_header, created_course):
    await client.post(f"/api/courses/{created_course.id}/start", headers=auth_header)
    response = await client.post(f"/api/courses/{created_course.id}/start", headers=auth_header)

    assert response.status_code == 400