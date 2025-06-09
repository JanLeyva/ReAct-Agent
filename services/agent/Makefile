build-docker: docker build -f Dockerfile -t agent .

run-docker: docker run -it -p 80:80 --env-file .env agent

test:
	uv run py.test -vv -W ignore