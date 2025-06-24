#!/bin/sh
if [ -z "${AWS_LAMBDA_RUNTIME_API}" ]; then
    echo "here"
    exec /usr/bin/aws-lambda-rie python -m awslambdaric $1
else
    echo "normal"
    exec python -m awslambdaric $1
fi