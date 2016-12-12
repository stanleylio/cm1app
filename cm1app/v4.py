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
sys.path.append('/home/nuc')
from node.authstuff import validate_message


logging.basicConfig(level=logging.DEBUG)

# requests.post(url,params=params,data={})

# public keys of authorized nodes
kmap = {'kmet-bbb':'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDN3PGFM+Ti+v/3CecZd5ls6G8OgVw4yFTtaFjVIDHmL51bC5ibKzelL7ZM+WU5WrRyeJmUNuK8IftFuQpQfJnGEhF7vpBpKhHQUK5SEMmcxPczKi0RWEelefE/IN1GlrnkDqQV7YMfasKSuhWq4OjgNsO0CxF18gatagPmOIiXZjXh7gMUF52d4faeU3oh5IxhO1+h+cx8jxRzovrNxicsbbYVOPc0pLw6WUIpDUsh7RDxxgiE3FCRdkxCYl8QJAhvtaXxbq/OnE8qRkTbi8aZ16D88qsaSjd31U2UmPqFJOuaYt8VDGYXw7rA9zmzufBxB2rfMRb2hSeb/qSv43c7 root@beaglebone',
        'kmet-bbb-wind':'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCvc6iktLLTAOFqOZCCUw2yJaL4U+rpg+Exy/LG6kEiv278WCIWpkv9Jo8cMyQrsUQtB38ZPhvCjThbCDuGom5gDjdN4cjZ2wtGztSWRnO83iQ5HKYcl+RLTxizP4KgGTkjbPRyf1pQLPw4jZxMNbGhqGSYP7hR/vqXaoz6KhsVuWORkCdClaUeP63jcDx+M4IOh8TjuwZZs7npoExmE4yEuj1YOTNdX59DYCtdGuidNbG1a8Vj/8Ai6Zt4BHY1gyvCwLocTv/6dxMP8w4fR68PvbmCidth2O7TYgPCFzTFHDcmDW6/LuaGfXrReExvpAjypcuPSIxBRMRNcDJdGeUF root@kmet-bbb-wind',
        'kmet-bbb2':'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDDyJJs/YWcu3iq4pzF18/Fa3fdJKRfmg4dTxdfCl6hhJ0uq1jzrFwtLx0+vKOL2SjR59sXufgw1tz2dqX/oqiN2yJkbxO0cqew9jaCFkkfNzr54FfzEp724uPS4QYPtP6IDx1jp5TioLG52l9AA+H1qgzm+svPylhGOzIBUWiRhCIuQxBtc3y3p7JzICm+cf3z0rEqJqkpa3xYRcSZWYeXz9Vj04mPGOXmulZG/fw05tVWPvyNYJ/Pa2l4MPuBzqXf5jzBBz7Vk3ZA1urMAXarodFFHEZai43gxrZqb9YxKBaFlKnRz+MUay/AOqRxcrPC8SQdL94QuY8r26k5bJV1 root@otg-bbb',
        'otg-met':'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCwWKFeLxMoujxt9ZaqMOS/4BBxI3X6Xwayt66p7ak3wvOhgULLuYKF6MSYQ3O2dwnCZyOm9xc2MdD/yAu7FcxrxLmJc1ysNH9fkW+SLtVV8T/j8k4sV8h0AhRhk26vP2aujPQCpn2OyzjZlgrIKTg0MC+nFAXNy/p5l65j6SGBMBDR52ro0Xm5orEyGgZT3hA497ErwyXbVZ/EqnmnoYFzll0OIz1GROQ+tAb2274EDByenSKk6tRKE5o/FxE3XVCNtjUpdtbsrVzFI/PbH0USjMtL3FdkK87zbx58HzbdMpNQVc1z1DFwNf87s/FWJ1uu9+3E8mw8utuwgDFVeS85 otg@otg-met',
        'glazerlab-i7nuc':'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC7Ic8W2GlUaaCwvt9k6NExrxqc89lZCYx4gQxEat0P1BO4qYp9JqtHKo8MQuYqkDK75nd/vuj3kygAwWv8AvQm935MrOh0LZ53TGhMEci4PoyY4X0XAUywUKM0Dur54lTe1g0EE9+jpcVPV6y3EmnvET78AkrURgDPbv8uCyVkQdKwBu3rpbRPjhC5srp7006heqFWfCLcs+tSt1SaMny4AafkWaPNhNkDb+sH/vgJIlpmM2Kt5Z074H0gABoWuX7gnW2CdhMXkjy0JYC7QnK3oSFhjms/zMHYp0uihk2ybTZv8HTuzCoHqxurjP6jVxFQNRl9xTCNeyyB2JiNRqon nuc@glazerlab-i7nuc',
        'base-001':'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDDxQo/IVvzvYQJNif7XDD2UOwrQjbY6azURNA4K6QU7xMvDGJ7cohkib5sneCnLiL836VlT3AJ3Nj1cM/0UftJv1h8H836jfSvtTTdDhDwDg150c32VRq1AN8yoUyQMKsfKduuAAcdpRtTnVO3brNHn9o+pn/p36uepKF+kZUVKf75Bh9VqCldAzCbYx+jhWyRItpEKYqOftlcyyoM1GCIx+1R1143qR+onN1wSa2+N8KO6XFN0lFmaVAUC4guRffESMg6GS12GuJLT8iOYhDMFeMrjS9/Fn14zW7oRIungxHGYPYXsju1UmxaArtWfqj2wK/mioqZFktKUg9IT7Ex root@base-001',
        'base-002':'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDAnKsvPuLQ0b3LtS8YJ28FEEZyRfY5GbpQSbbWjqojBn2AhbXIBo6D7D2c2j2OOcRkh7+3dyX7nyCjn0Yojb21sZxrW26jmT+7Zbi4N88Hexqd20RIjKeECA5ahUq8Kk+vG9qZvozXUR4RLyopn8bQ5240WlenNUxD2am81SxJzfJsMWeQniff9uiCnab+EZrbTn/CxgQex9cvgrbsRtoEUQwpO9bnXJpPhjGZdF/1PfDmDJvsd0NUa/SU8xTCh7ASLfQIopvxq9GuRN2GyfnW9HO4r0YBuBKt4oixJJRVlRF6RLv0LHTjQVEuRmmPwTEsGkwywGPn/9asbS4oBPF5 root@base-002',
        'base-003':'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC9pNGjCrQtHdhV87rJfud1uwZyhG4XzW4XMkn2f2KdH0pVRK6iEDuw4Z8tcgHTPiHckdu/FkE+4rV9zzbPR7w/9jTZOf2YI64gFu98qPcLoJOImT7vI5BEagAyvW7pyjTnlmo0+rQeti8B4tb48/ScJrLVQbMKK7eCXebwEYL89Ie9mGpM2hxs9LKrqYjrKIfs33oottKzi774yQ8jhO4CIcYKdkdEOPi1RgA1riYDp3Rz34rlotJ0MQpCxqQjwAXntVvplqfFpU1iG21kQu6U9ro0YFpVgpyyw3Jomqv5rbeMYG9C0fMWBQKXFgocxiQdinsuvMA81++iiKAXFHov nuc@base-003',
        'base-004':'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCuAIuai8QXOsi2KTzJrNVBFXvWMvqUQ5QKGYVzo7/Qr6gxj8xZZCcdukFFkTrCvHEsl7J0gHNsdwakTs+jVw8F7km4MPozGAMXoDEV/wWcXIxoaObUjRYsoUjArWrjsw3HlMbM+juKCYOPQsk8nYLpqv3BQ0Vc6p36OVDmIUfqNpwYxb6lpjgGo6j3npg+zgc8wfa5OyOBSEB5nkYN9k2WvJlKRVtDgvb4LA1lvTthPwb8z8jwFI2AV/Dr5SB1+miTQKbLmav/R6Uzpgxlc8mAMg9xz4NVQYm5t/uuCfigSG9S7oYg2FewNElO3zvykuTYHlVlFK6m55LaTE0gLSPr nuc@base-004',
        'base-005':'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDxV+erlyNnJIZvhQHcYlajCuA6o/+geEnbruDMxZy0a8H6MM5J4298T/8G8RLjyJBelzX8TcwBStj8dkMbdNOTgBrSzh9yzzP9hw+EBqwwnm/9dACLXEehBqqdy65GSpXDR37oR1ik0+u7s7sjqnZkJgDUzcFdGkG2No40LEa8yp7DR3YWz3feUBBIc96FjyOAtsu/lWYrJAoL7lwwc3En1xjslpap/s2lnwkh652/CVccevENh+cfIcPWgJvykiUNxQlLFmy+HUQZcGDa6iFXblKNLxMSyOhmmH93ixam1aiSXpckIXGtjHqnF4C2/1RJjBjlJdfD6vwuQNRdRAmF root@base-005'}


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
