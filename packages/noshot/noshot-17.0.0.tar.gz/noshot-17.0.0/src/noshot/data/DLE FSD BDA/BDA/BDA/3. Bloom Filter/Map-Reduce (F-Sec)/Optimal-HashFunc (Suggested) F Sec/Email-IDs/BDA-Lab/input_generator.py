import random
import string

random.seed(42)

DOMAINS = ["example.com", "test.in", "mail.com"]
CHARACTER_SET = string.ascii_lowercase + string.digits
with open("input.txt", "w") as f:
    for _ in range(50):
        local_part = ''.join(random.choice(CHARACTER_SET) for _ in range(8))
        domain = random.choice(DOMAINS)
        email = local_part + "@" + domain
        f.write(email + "\n")