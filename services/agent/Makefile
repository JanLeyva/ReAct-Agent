build: docker build -f Dockerfile -t agent_alpine .

run-docker: docker run -it -p 80:80 --env-file /.env agent_alpine

test:
	uv run py.test -vv -W ignore