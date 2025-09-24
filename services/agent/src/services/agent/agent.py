# https://developers.llamaindex.ai/python/framework/understanding/workflows/basic_flow/
# 1st party
from typing import Any

# internal libs
from src.services.agent.tools import get_coordinates_from_street, get_restaurant_recommendation_from_text_and_coordinates, get_restaurant_recommendation_from_text
from src.shared.llm.factory import llm

# 3rd party
from llama_index.core.workflow import (
    Workflow,
    step,
    Event,
    StartEvent,
    StopEvent,
)
from llama_index.core.llms.llm import LLM


class SearchWithLocationEvent(Event):
    query: str

class SearchWithoutLocationEvent(Event):
    query: str

class GetCoordinatesEvent(Event):
    query: str

class InvalidIntentEvent(Event):
    pass

class ShowAnswerEvent(Event):
    answer: Any

class RestaurantWorkflow(Workflow):
    def __init__(
        self,
        *args: Any,
        llm: LLM | None = None,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self.llm = llm

    @step
    def router(self, ev: StartEvent) -> GetCoordinatesEvent | SearchWithoutLocationEvent | InvalidIntentEvent:
        """
        Router step to determine the intent of the query.
        """
        query = ev.input
        prompt = f"""
            You are a router agent. Your purpose is to determine the intent of the user's query.
            The valid intents are related to searching for restaurants in Barcelona.
            If the user is asking for a restaurant with a location (e.g. 'near a place or street'), you should return "search_restaurant_with_location".
            If the user is asking for a restaurant without a location (e.g. 'a type of restaurant'), you should return "search_restaurant_without_location".
            Otherwise, you should return "invalid_intent".

            Query: {query}
        """
        response = self.llm.complete(prompt)
        if "search_restaurant_with_location" in response.text:
            return GetCoordinatesEvent(query=query)
        elif "search_restaurant_without_location" in response.text:
            return SearchWithoutLocationEvent(query=query)
        return InvalidIntentEvent()

    @step
    def get_coordinates(self, ev: GetCoordinatesEvent) -> SearchWithLocationEvent:
        """
        Step to get coordinates from a street name.
        """
        coordinates = get_coordinates_from_street(ev.query)
        return SearchWithLocationEvent(query=ev.query, payload={"coordinates": coordinates})

    @step
    def search_with_location(self, ev: SearchWithLocationEvent) -> ShowAnswerEvent:
        """
        Step to search for a restaurant with location.
        """
        coordinates = ev.payload["coordinates"]
        answer = get_restaurant_recommendation_from_text_and_coordinates(ev.query, [coordinates['lat'], coordinates['lng']], 1000)
        return ShowAnswerEvent(answer=answer)

    @step
    def search_without_location(self, ev: SearchWithoutLocationEvent) -> ShowAnswerEvent:
        """
        Step to search for a restaurant without location.
        """
        answer = get_restaurant_recommendation_from_text(ev.query)
        return ShowAnswerEvent(answer=answer)

    @step
    def handle_invalid_intent(self, ev: InvalidIntentEvent) -> StopEvent:
        return StopEvent(result="I can only help you with restaurant recommendations in Barcelona.")

    @step
    def show_answer(self, ev: ShowAnswerEvent) -> StopEvent:
        """
        Step to show the answer to the user.
        """
        prompt = f"""
            You are a helpful assistant. Your purpose is to show the answer to the user in a friendly way.
            Answer: {ev.answer}
        """
        response = self.llm.complete(prompt)
        return StopEvent(result=response.text)

