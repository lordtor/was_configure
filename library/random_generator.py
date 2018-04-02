import string
import random
from ansible.module_utils.basic import AnsibleModule


def random_generator(size, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


module = AnsibleModule(
    argument_spec=dict(
        size=dict(required=True, type='int')
    )
)
size = module.params.get('size')

try:
    random_generator(size)
    success = True
    ret_msg = str(random_generator(size))
except KeyError:
    success = False
    ret_msg = "Error"

if success:
    module.exit_json(msg=ret_msg)
else:
    module.fail_json(msg=ret_msg)

if __name__ == "__main__":
    main()
