build:
	docker build -f Dockerfile -t agent_alpine .

run-docker: docker run -it -p 8000:8000 agent

test:
	uv run py.test -vv -W ignore