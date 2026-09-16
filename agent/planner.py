from brain.router import route_command


class Planner:

    def plan(self, user_text):
        route = route_command(user_text)

        return {
            "type": route["type"],
            "query": route["query"],
            "command": route["command"],
        }