from assertpy import assert_that
from sqlmodel import Session


def test_entity_with_session(get_session: Session):
    assert_that(True).is_true()
