# https://developers.llamaindex.ai/python/framework/understanding/workflows/basic_flow/
# 1st party
from typing import Any

# internal libs
# from src.services.agent.tools import get_coordinates_from_street, get_restaurant_recommendation_from_text_and_coordinates, get_restaurant_recommendation_from_text
# from src.shared.llm.factory import llm

from src.shared.templates.prompts import REWRITE, ROUTER_PROMPT, ANSWER_PROMPT

# 3rd party
from llama_index.core.workflow import (
    Workflow,
    step,
    Event,
    StartEvent,
    StopEvent,
)
from llama_index.core.llms.llm import LLM


class Rewrite(Event):
    query: str
    rewrite: str

class SearchWithLocationEvent(Event):
    query: str
    coordinates: dict

class SearchWithoutLocationEvent(Event):
    query: str

class GetCoordinatesEvent(Event):
    query: str

class InvalidIntentEvent(Event):
    pass

class ShowAnswerEvent(Event):
    answer: Any
class RestaurantWorkflow(Workflow):
    def __init__(self, llm: LLM, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.llm = llm

    @step
    async def rewrite(self, ev: StartEvent) -> Rewrite:
        query = ev.input
        prompt = REWRITE.format(query=query, context="")
        rewrite = self.llm.complete(prompt)

        return Rewrite(query=query, rewrite=rewrite.text)

    @step
    async def router(self, ev: Rewrite) -> GetCoordinatesEvent | InvalidIntentEvent | SearchWithoutLocationEvent:
        query = ev.query
        rewrite = ev.rewrite
        prompt = ROUTER_PROMPT.format(query=query, rewrite=rewrite)
        response = self.llm.complete(prompt)

        if "search_restaurant_with_location" in response.text:
            return GetCoordinatesEvent(query=rewrite)
        elif "search_restaurant_without_location" in response.text:
            return SearchWithoutLocationEvent(query=rewrite)
        return InvalidIntentEvent()

    @step
    async def get_coordinates(self, ev: GetCoordinatesEvent) -> SearchWithLocationEvent:
        print(ev.query)
        print("get_coordinates")
        coordinates = {"lat": 41.4036299, "lng": 2.1743558} # mock
        return SearchWithLocationEvent(query=ev.query, coordinates=coordinates)
    
    @step
    async def search_with_location(self, ev: SearchWithLocationEvent) -> ShowAnswerEvent:
        """
        Step to search for a restaurant with location.
        """
        coordinates = ev.coordinates
        print("search_with_location")
        # answer = get_restaurant_recommendation_from_text_and_coordinates(ev.query, [coordinates['lat'], coordinates['lng']], 1000)
        answer = "mock answer with location"
        return ShowAnswerEvent(answer=answer)

    @step
    async def search_without_location(self, ev: SearchWithoutLocationEvent) -> ShowAnswerEvent:
        """
        Step to search for a restaurant without location.
        """
        # answer = get_restaurant_recommendation_from_text(ev.query)
        print("search_without_location")
        answer = "mock answer without location"
        return ShowAnswerEvent(answer=answer)
    
    @step
    async def handle_invalid_intent(self, ev: InvalidIntentEvent) -> StopEvent:
        return StopEvent(result="I can only help you with restaurant recommendations in Barcelona.")
    
    @step
    def show_answer(self, ev: ShowAnswerEvent) -> StopEvent:
        """
        Step to show the answer to the user.
        """
        prompt =  ANSWER_PROMPT.format(ev.answer)
        response = self.llm.complete(prompt)
        return StopEvent(result=response.text)