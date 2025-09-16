import argparse

from c8yrc.rest_client.c8y_rest_client import C8yRestClient

#INSTALL_IMAGE_FROM_C8Y $C8Y_REST_USER_NAME $C8Y_REST_USER_PASSWORD $IX $ENV_YAML_FILE_NAME $MENDER_ARTIFACT_URL

parser = argparse.ArgumentParser(prog='cube_software_update_test.py')
subparsers = parser.add_subparsers()
subparsers.required = True   # the fudge
subparsers.dest = 'command'
subparser = subparsers.add_parser("INSTALL_IMAGE_FROM_C8Y", help="run Install Cube Image")
subparser.add_argument('rest_user_name', help="Rest User of cumulocity")
subparser.add_argument('rest_user_password', help="Rest User password of cumulocity")
subparser.add_argument('device_serial_number', help="Index of the node on the configuration file")


args = parser.parse_args()

c8y_serial_number = f'CB1-{args.device_serial_number}'.lower()
my_c8y_api = C8yRestClient(c8y_serial_number=c8y_serial_number,
                           user=args.rest_user_name, password=args.rest_user_password,
                           url='https://main.dm-zz-q.ioee10-cloud.com/', tenant='t2700')

fw = my_c8y_api.get_available_containers(my_c8y_api.cy8_device.type)


