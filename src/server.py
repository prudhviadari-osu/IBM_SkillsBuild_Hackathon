from fastapi import FastAPI
import socket

# Support both package execution (`uvicorn src.server:app`) and local module execution (`uvicorn server:app` from src/)
try:
    from src.canvas_client import dump_canvas
    from src.study_engine import StudyEngine
except ModuleNotFoundError:
    from canvas_client import dump_canvas
    from study_engine import StudyEngine

app = FastAPI()

engine = StudyEngine()


@app.get("/dump")
def dump_endpoint():

    data = dump_canvas()

    docs = []

    for course in data["courses"]:
        if course["syllabus"]:
            docs.append(course["syllabus"])

        for a in course["assignments"]:
            if a.get("description"):
                docs.append(a["description"])

    engine.index(docs)

    return data


@app.get("/search")
def search_endpoint(q: str):

    return {
        "results": engine.search(q)
    }


if __name__ == "__main__":
    import uvicorn

    host = "127.0.0.1"
    start_port = 8000
    port = start_port

    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if sock.connect_ex((host, port)) != 0:
                break
        port += 1

    if port != start_port:
        print(f"Port {start_port} is in use, starting on {port} instead.")

    uvicorn.run(app, host=host, port=port)
