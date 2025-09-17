"""
Test controller for request/response handling
"""

from pygrestqlambda.controller import Controller


def test_get_single_record():
    """
    Test GET to retrieve a single record
    """

    controller = Controller(event={
        "httpMethod": "GET",
    })
    response = controller.run()

    assert response.status_code == 200


def test_post():
    """
    Test POST to create a new record
    """

    controller = Controller(event={
        "httpMethod": "POST",
    })
    response = controller.run()

    assert response.status_code == 201


def test_put():
    """
    Test PUT to create a new record
    """

    controller = Controller(event={
        "httpMethod": "PUT",
    })
    response = controller.run()

    assert response.status_code == 201


def test_patch():
    """
    Test PATCH to edit an existing record
    """

    controller = Controller(event={
        "httpMethod": "PATCH",
    })
    response = controller.run()

    assert response.status_code == 200


def test_delete():
    """
    Test DELETE to remove an existing record
    """

    controller = Controller(event={
        "httpMethod": "DELETE",
    })
    response = controller.run()

    assert response.status_code == 204
