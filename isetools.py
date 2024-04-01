import yaml
import asyncio
import base64
import os
import path
import argparse

my_path = path.Path(__file__).parent.abspath()
with open(f"{my_path / 'settings.yml'}", "r") as f:
    settings = yaml.safe_load(f)


# Get the password from the command line argument and decode it
def decoder(encoded_password):
    padding = "=" * ((4 - len(encoded_password) % 4) % 4)  # deterimine padding to add back
    pw = base64.b64decode(encoded_password + padding)  # add required padding back to encoded pw
    pw = pw.decode("utf-8")  # convert back from Unicode
    return pw


def encoder(password):
    encoded_password = base64.b64encode(password.encode("utf-8"))
    return encoded_password

# Loads arguments to parse from settings file, loaded from the 'parameters' slice of the 'executables' dictionay
def argument_loader(arg_map: dict, parser: argparse.ArgumentParser):
    # args_list = []
    for key, value in arg_map.items():
        argument = value["argument"]
        help_text = value["help"]
        parser.add_argument(f'--{key}', f'-{argument}', help=help_text, required=True)
    
    return parser

class AsyncConsumer:
    def __init__(self, number_of_consumers: int, consumer, items):
        self.number_of_consumers = number_of_consumers
        self.queue = asyncio.Queue()
        self.out_queue = asyncio.Queue()
        self.consumer = consumer
        self.items = items
        self.endpiointData = []
        # self.consumers_list = self.consume(self.number_of_consumers)

    async def produce(self):
        for item in self.items:
            await self.queue.put(item)
            # print(f'producing {item}...') only for debugging

    async def run(self):
        producer = asyncio.create_task(self.produce())
        await producer
        # consumers = self.consume(self.number_of_consumers)
        print(f"Async starting with {self.number_of_consumers}")
        self.endpiointData = await asyncio.gather(
            *[self.consumer(self.queue, self.out_queue) for _ in range(self.number_of_consumers)],
            return_exceptions=True,
        )

        return self.endpiointData
