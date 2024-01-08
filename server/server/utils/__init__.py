import uuid


def convert_to_uuid4(uuid_string):
    # Add hyphens to the UUID string
    uuid_with_hyphens = uuid_string[:8] + '-' + uuid_string[8:12] + '-' + \
        uuid_string[12:16] + '-' + uuid_string[16:20] + '-' + uuid_string[20:]

    # Convert the string to a UUID4
    return str(uuid.UUID(uuid_with_hyphens, version=4))


def is_valid_uuid4(uuid_string):
    try:
        uuid_obj = uuid.UUID(uuid_string, version=4)
    except ValueError:
        # If it's a value error, then the string
        # is not a valid hex code for a UUID.
        return False

    # If the uuid_obj.verson is not 4 then this isn't a UUID4
    return uuid_obj.version == 4
