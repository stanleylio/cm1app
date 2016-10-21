# -*- coding: utf-8 -*-
# experimental, sandbox-class stuff
#
# Stanley H.I. Lio
# hlio@hawaii.edu
# All Rights Reserved. 2016
from cm1app import app
from flask import request
from datetime import datetime
import logging,traceback,sys
sys.path.append('/home/nuc/node')
from authstuff import validate_message


logging.basicConfig(level=logging.DEBUG)

# requests.post(url,params=params,data={})

# public keys of authorized nodes
kmap = {'kmet-bbb':'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDN3PGFM+Ti+v/3CecZd5ls6G8OgVw4yFTtaFjVIDHmL51bC5ibKzelL7ZM+WU5WrRyeJmUNuK8IftFuQpQfJnGEhF7vpBpKhHQUK5SEMmcxPczKi0RWEelefE/IN1GlrnkDqQV7YMfasKSuhWq4OjgNsO0CxF18gatagPmOIiXZjXh7gMUF52d4faeU3oh5IxhO1+h+cx8jxRzovrNxicsbbYVOPc0pLw6WUIpDUsh7RDxxgiE3FCRdkxCYl8QJAhvtaXxbq/OnE8qRkTbi8aZ16D88qsaSjd31U2UmPqFJOuaYt8VDGYXw7rA9zmzufBxB2rfMRb2hSeb/qSv43c7 root@beaglebone',
        'kmet-bbb-wind':'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCvc6iktLLTAOFqOZCCUw2yJaL4U+rpg+Exy/LG6kEiv278WCIWpkv9Jo8cMyQrsUQtB38ZPhvCjThbCDuGom5gDjdN4cjZ2wtGztSWRnO83iQ5HKYcl+RLTxizP4KgGTkjbPRyf1pQLPw4jZxMNbGhqGSYP7hR/vqXaoz6KhsVuWORkCdClaUeP63jcDx+M4IOh8TjuwZZs7npoExmE4yEuj1YOTNdX59DYCtdGuidNbG1a8Vj/8Ai6Zt4BHY1gyvCwLocTv/6dxMP8w4fR68PvbmCidth2O7TYgPCFzTFHDcmDW6/LuaGfXrReExvpAjypcuPSIxBRMRNcDJdGeUF root@kmet-bbb-wind',
        'otg-bbb':'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDDyJJs/YWcu3iq4pzF18/Fa3fdJKRfmg4dTxdfCl6hhJ0uq1jzrFwtLx0+vKOL2SjR59sXufgw1tz2dqX/oqiN2yJkbxO0cqew9jaCFkkfNzr54FfzEp724uPS4QYPtP6IDx1jp5TioLG52l9AA+H1qgzm+svPylhGOzIBUWiRhCIuQxBtc3y3p7JzICm+cf3z0rEqJqkpa3xYRcSZWYeXz9Vj04mPGOXmulZG/fw05tVWPvyNYJ/Pa2l4MPuBzqXf5jzBBz7Vk3ZA1urMAXarodFFHEZai43gxrZqb9YxKBaFlKnRz+MUay/AOqRxcrPC8SQdL94QuY8r26k5bJV1 root@otg-bbb',
        'glazerlab-i7nuc':'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC7Ic8W2GlUaaCwvt9k6NExrxqc89lZCYx4gQxEat0P1BO4qYp9JqtHKo8MQuYqkDK75nd/vuj3kygAwWv8AvQm935MrOh0LZ53TGhMEci4PoyY4X0XAUywUKM0Dur54lTe1g0EE9+jpcVPV6y3EmnvET78AkrURgDPbv8uCyVkQdKwBu3rpbRPjhC5srp7006heqFWfCLcs+tSt1SaMny4AafkWaPNhNkDb+sH/vgJIlpmM2Kt5Z074H0gABoWuX7gnW2CdhMXkjy0JYC7QnK3oSFhjms/zMHYp0uihk2ybTZv8HTuzCoHqxurjP6jVxFQNRl9xTCNeyyB2JiNRqon nuc@glazerlab-i7nuc',
        'base-003':'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC9pNGjCrQtHdhV87rJfud1uwZyhG4XzW4XMkn2f2KdH0pVRK6iEDuw4Z8tcgHTPiHckdu/FkE+4rV9zzbPR7w/9jTZOf2YI64gFu98qPcLoJOImT7vI5BEagAyvW7pyjTnlmo0+rQeti8B4tb48/ScJrLVQbMKK7eCXebwEYL89Ie9mGpM2hxs9LKrqYjrKIfs33oottKzi774yQ8jhO4CIcYKdkdEOPi1RgA1riYDp3Rz34rlotJ0MQpCxqQjwAXntVvplqfFpU1iG21kQu6U9ro0YFpVgpyyw3Jomqv5rbeMYG9C0fMWBQKXFgocxiQdinsuvMA81++iiKAXFHov nuc@base-003',
        'base-004':'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCuAIuai8QXOsi2KTzJrNVBFXvWMvqUQ5QKGYVzo7/Qr6gxj8xZZCcdukFFkTrCvHEsl7J0gHNsdwakTs+jVw8F7km4MPozGAMXoDEV/wWcXIxoaObUjRYsoUjArWrjsw3HlMbM+juKCYOPQsk8nYLpqv3BQ0Vc6p36OVDmIUfqNpwYxb6lpjgGo6j3npg+zgc8wfa5OyOBSEB5nkYN9k2WvJlKRVtDgvb4LA1lvTthPwb8z8jwFI2AV/Dr5SB1+miTQKbLmav/R6Uzpgxlc8mAMg9xz4NVQYm5t/uuCfigSG9S7oYg2FewNElO3zvykuTYHlVlFK6m55LaTE0gLSPr nuc@base-004'}


@app.route('/api/4',methods=['POST'])
def s4submit():
    try:
        # ?=& queries
        #request.args.get('client',None)

        # form data
        ts = request.form['ts']
        src = request.form['src']
        msg = request.form['msg']
        sig = request.form['sig']
        if src not in kmap:
            return 'unknown client'
        if not validate_message(msg,sig,kmap[src]):
            return 'bad signature'
        #ReceptionTime,TransmissionTime,Source,Message
        with open('/home/nuc/data/api/4/tsraw.txt','a',0) as f:
            f.write('{},{},{},{}\n'.format(datetime.utcnow().isoformat(),ts,src,msg))
            return '{},ok'.format(datetime.utcnow().isoformat())
    except:
        logging.debug(traceback.format_exc())
        return ''
