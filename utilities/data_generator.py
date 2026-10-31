"""Generate unique, synthetic customer data so each execution is independent."""
import secrets
import string
from faker import Faker

fake = Faker("en_US")


def generate_customer ( registration_defaults ) :
    """Generate unique customer details; keep only the password configurable."""
    suffix = secrets.token_hex(4)
    username = f"qa_{suffix}"
    password = registration_defaults["password"]
    return {
        "first_name" : fake.first_name() ,
        "last_name" : fake.last_name() ,
        "street" : fake.street_address() ,
        "city" : fake.city() ,
        "state" : fake.state_abbr() ,
        "zip_code" : fake.postcode() ,
        "phone" : fake.numerify(text="###-###-####") ,
        # Synthetic 9-digit value only; never use a real person's SSN.
        "ssn" : "".join(secrets.choice(string.digits) for _ in range(9)) ,
        "username" : username ,
        "password" : password ,
    }
