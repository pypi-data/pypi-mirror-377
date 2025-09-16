from src.domain.flag import Flag


def test_user_can_create_a_flag_with_its_name_and_value():
    """
    Given a `flag name` as string
    When I initialize a `Flag` with this name and some default value
    Then I'm expecting a `Flag` initialized with the default value.
    """
    # Given
    flag_name = "my_first_flag"
    # When
    flag = Flag(name=flag_name, value=True)
    # Then
    assert flag.name == flag_name, "Something went very wrong!"
    assert flag.value is True
    assert flag.desc is None
