import logging
import sys
from src.llm.factory import llm

import asyncio
from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
    Workflow,
    step,
    Context
)
from llama_index.core.workflow import Event
# in case we want to draw our worglow graph
from llama_index.utils.workflow import draw_all_possible_flows
# to draw
# draw_all_possible_flows(
#     basic_workflow, 
#     filename="workflows/basic_workflow.html"
# )



# let's build a workflow step by step
class FirstEvent(Event):
    first_output: str

class SecondEvent(Event):
    second_output: str

# define Workflow - Basic
# class MyWorkflow(Workflow):
#     @step
#     async def step_one(self, ev: StartEvent) -> FirstEvent:
#         print(ev.first_input)
#         return FirstEvent(first_output="First step complete.")

#     @step
#     async def step_two(self, ev: FirstEvent) -> SecondEvent:
#         print(ev.first_output)
#         return SecondEvent(second_output="Second step complete.")

#     @step
#     async def step_three(self, ev: SecondEvent) -> StopEvent:
#         print(ev.second_output)
#         return StopEvent(result="Workflow complete.")



# class MyWorkflow(Workflow):
#     # declare a function as a step
#     @step
#     async def my_step(self, ev: StartEvent) -> StopEvent:
#         # do something here
#         return StopEvent(result="Hello, world!")


# Loop Workflow
import random
class LoopEvent(Event):
    loop_output: str

class MyWorkflow(Workflow):
    @step
    async def step_one(self, ev: StartEvent | LoopEvent) -> FirstEvent | LoopEvent:
        if random.randint(0, 1) == 0:
            print("Bad thing happened")
            return LoopEvent(loop_output="Back to step one.")
        else:
            print("Good thing happened")
            return FirstEvent(first_output="First step complete.")

    @step
    async def step_two(self, ev: FirstEvent) -> SecondEvent:
        print(ev.first_output)
        return SecondEvent(second_output="Second step complete.")

    @step
    async def step_three(self, ev: SecondEvent) -> StopEvent:
        print(ev.second_output)
        return StopEvent(result="Workflow complete.")
    

# Branching
class BranchA1Event(Event):
    payload: str

class BranchA2Event(Event):
    payload: str

class BranchB1Event(Event):
    payload: str

class BranchB2Event(Event):
    payload: str


class BranchWorkflow(Workflow):
    @step
    async def start(self, ev: StartEvent) -> BranchA1Event | BranchB1Event:
        if random.randint(0, 1) == 0:
            print("Go to branch A")
            return BranchA1Event(payload="Branch A")
        else:
            print("Go to branch B")
            return BranchB1Event(payload="Branch B")

    @step
    async def step_a1(self, ev: BranchA1Event) -> BranchA2Event:
        print(ev.payload)
        return BranchA2Event(payload=ev.payload)

    @step
    async def step_b1(self, ev: BranchB1Event) -> BranchB2Event:
        print(ev.payload)
        return BranchB2Event(payload=ev.payload)

    @step
    async def step_a2(self, ev: BranchA2Event) -> StopEvent:
        print(ev.payload)
        return StopEvent(result="Branch A complete.")

    @step
    async def step_b2(self, ev: BranchB2Event) -> StopEvent:
        print(ev.payload)
        return StopEvent(result="Branch B complete.")
    
# Combining diferent type events
class StepAEvent(Event):
    query: str

class StepACompleteEvent(Event):
    result: str

class StepBEvent(Event):
    query: str

class StepBCompleteEvent(Event):
    result: str

class StepCEvent(Event):
    query: str

class StepCCompleteEvent(Event):
    result: str

class ConcurrentFlow(Workflow):
    @step
    async def start(
        self, ctx: Context, ev: StartEvent
    ) -> StepAEvent | StepBEvent | StepCEvent:
        ctx.send_event(StepAEvent(query="Query 1"))
        ctx.send_event(StepBEvent(query="Query 2"))
        ctx.send_event(StepCEvent(query="Query 3"))

    @step
    async def step_a(self, ctx: Context, ev: StepAEvent) -> StepACompleteEvent:
        print("Doing something A-ish")
        return StepACompleteEvent(result=ev.query)

    @step
    async def step_b(self, ctx: Context, ev: StepBEvent) -> StepBCompleteEvent:
        print("Doing something B-ish")
        return StepBCompleteEvent(result=ev.query)

    @step
    async def step_c(self, ctx: Context, ev: StepCEvent) -> StepCCompleteEvent:
        print("Doing something C-ish")
        return StepCCompleteEvent(result=ev.query)

    @step
    async def step_three(
        self,
        ctx: Context,
        ev: StepACompleteEvent | StepBCompleteEvent | StepCCompleteEvent,
    ) -> StopEvent:
        print("Received event ", ev.result)

        # wait until we receive 3 events
        events = ctx.collect_events(
            ev,
            [StepCCompleteEvent, StepACompleteEvent, StepBCompleteEvent],
        )
        if (events is None):
            return None

        # do something with all 3 results together
        print("All events received: ", events)
        return StopEvent(result="Done")
    

# Now let's do a Streaming Workglow
class FirstEvent(Event):
    first_output: str

class SecondEvent(Event):
    second_output: str
    response: str

class TextEvent(Event):
    delta: str

class ProgressEvent(Event):
    msg: str


class MyWorkflow(Workflow):
    @step
    async def step_one(self, ctx: Context, ev: StartEvent) -> FirstEvent:
        ctx.write_event_to_stream(ProgressEvent(msg="Step one is happening"))
        return FirstEvent(first_output="First step complete.")

    @step
    async def step_two(self, ctx: Context, ev: FirstEvent) -> SecondEvent:
        # llm = llm
        generator = await llm.astream_complete(
            "Please give me the first 50 words of Moby Dick, a book in the public domain."
        )
        async for response in generator:
            # Allow the workflow to stream this piece of response
            ctx.write_event_to_stream(TextEvent(delta=response.delta))
        return SecondEvent(
            second_output="Second step complete, full response attached",
            response=str(response),
        )

    @step
    async def step_three(self, ctx: Context, ev: SecondEvent) -> StopEvent:
        ctx.write_event_to_stream(ProgressEvent(msg="Step three is happening"))
        return StopEvent(result="Workflow complete.")


async def main():
    # instantiate the workflow
    workflow = MyWorkflow(timeout=10, verbose=False)
    # run the workflow
    # result = await workflow.run(first_input="Start the workflow.")
    # result = await workflow.run(first_input="Start the workflow.")
    handler = workflow.run(first_input="Start the workflow.")
    async for ev in handler.stream_events():
        if isinstance(ev, ProgressEvent):
            print(ev.msg)
        if isinstance(ev, TextEvent):
            print(ev.delta, end="")

    final_result = await handler
    print("Final result = ", final_result)

    draw_all_possible_flows(
    workflow, 
    filename="workflow.html"
)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
